from __future__ import annotations

import ast
import importlib
import importlib.metadata
import inspect
import re
import sys
import sysconfig
import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / "tests" / "parity" / "allowlist.toml"
DOC_PATHS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("**/*"))]

MODULES = [
    "alarm",
    "analogio",
    "bitbangio",
    "board",
    "busio",
    "countio",
    "digitalio",
    "keypad",
    "microcontroller",
    "micropython",
    "neopixel_write",
    "pulseio",
    "pwmio",
    "rainbowio",
    "rotaryio",
    "socketpool",
    "supervisor",
    "sys",
    "time",
    "watchdog",
    "wifi",
]

DUnder_API = {
    "__bool__",
    "__contains__",
    "__enter__",
    "__exit__",
    "__getitem__",
    "__iter__",
    "__len__",
    "__next__",
    "__setitem__",
}


@dataclass(frozen=True)
class Case:
    module: str
    symbol: str
    kind: str
    stub: Any = None

    @property
    def full_symbol(self) -> str:
        return f"{self.module}.{self.symbol}"


@dataclass(frozen=True)
class Result:
    ok: bool
    detail: str
    category: str


class StubConstant:
    pass


class StubFunction:
    def __init__(self, signatures: list[inspect.Signature] | None = None):
        self.__signatures__ = signatures or []
        if self.__signatures__:
            self.__signature__ = self.__signatures__[0]

    def add_signature(self, signature: inspect.Signature) -> None:
        self.__signatures__.append(signature)
        if not hasattr(self, "__signature__"):
            self.__signature__ = signature

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class _DefaultExpr:
    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return self.expr


def pytest_generate_for_module(metafunc, module_name: str) -> None:
    if "case" not in metafunc.fixturenames:
        return
    cases = collect_cases(module_name)
    ids = [case.full_symbol for case in cases]
    metafunc.parametrize("case", cases, ids=ids)


def assert_case(case: Case) -> None:
    allowlist = load_allowlist()
    result = check_case(case)
    allowed = case.full_symbol in allowlist
    if result.ok and allowed:
        raise AssertionError(
            f"{case.full_symbol} is allowlisted but now matches the CircuitPython stub; "
            "remove the stale allowlist entry."
        )
    if not result.ok and not allowed:
        raise AssertionError(result.detail)


def collect_cases(module_name: str) -> list[Case]:
    try:
        stub_module = load_stub_module(module_name)
    except Exception as exc:
        return [Case(module_name, "__stub__", "setup", exc)]

    try:
        layer_module = import_layer_module(module_name)
    except Exception as exc:
        return [Case(module_name, "__layer_import__", "setup", exc)]

    cases: list[Case] = []
    for name, stub_value in public_items(stub_module):
        kind = kind_of(stub_value)
        cases.append(Case(module_name, name, kind, stub_value))
        if kind != "class":
            continue
        layer_class = getattr(layer_module, name, None)
        if not inspect.isclass(layer_class):
            continue
        for member_name, member_value in public_class_items(stub_value):
            member_kind = kind_of(member_value)
            cases.append(
                Case(
                    module_name,
                    f"{name}.{member_name}",
                    member_kind,
                    member_value,
                )
            )
    return cases


def check_case(case: Case) -> Result:
    if case.kind == "setup":
        return Result(False, f"{case.full_symbol}: {case.stub}", "setup")

    try:
        layer_module = import_layer_module(case.module)
    except Exception as exc:
        return Result(False, f"{case.module}: could not import layer module: {exc}", "missing")

    parts = case.symbol.split(".")
    parent: Any = layer_module
    for part in parts[:-1]:
        parent = getattr(parent, part, None)
        if parent is None:
            return Result(False, f"{case.full_symbol}: missing parent {part}", "missing")

    name = parts[-1]
    missing = object()
    layer_value = getattr(parent, name, missing)
    if layer_value is missing:
        return Result(False, f"{case.full_symbol}: missing", "missing")

    try:
        layer_static = inspect.getattr_static(parent, name)
    except AttributeError:
        layer_static = layer_value

    if case.kind == "class":
        if not inspect.isclass(layer_value):
            return Result(False, f"{case.full_symbol}: expected class, found {type(layer_value).__name__}", "kind")
        return Result(True, "provided", "ok")

    if case.kind == "property":
        if not isinstance(layer_static, property):
            return Result(False, f"{case.full_symbol}: expected property, found {type(layer_static).__name__}", "kind")
        return Result(True, "provided", "ok")

    if case.kind == "function":
        unwrapped = unwrap_descriptor(layer_static)
        if isinstance(unwrapped, property):
            return Result(False, f"{case.full_symbol}: expected method/function, found property", "kind")
        if not callable(unwrapped):
            return Result(False, f"{case.full_symbol}: expected callable, found {type(layer_value).__name__}", "kind")
        return compare_signatures(case.full_symbol, unwrapped, case.stub)

    return Result(True, "provided", "ok")


def compare_signatures(symbol: str, layer_func: Any, stub_func: Any) -> Result:
    try:
        layer_shape = signature_shape(inspect.signature(layer_func))
    except Exception as exc:
        return Result(False, f"{symbol}: could not inspect layer signature: {exc}", "signature")

    stub_signatures = candidate_signatures(stub_func)
    stub_shapes = [signature_shape(signature) for signature in stub_signatures]
    if layer_shape in stub_shapes:
        return Result(True, "provided", "ok")

    expected = " or ".join(format_shape(shape) for shape in stub_shapes)
    actual = format_shape(layer_shape)
    return Result(
        False,
        f"{symbol}: signature mismatch; expected {expected}, found {actual}",
        "signature",
    )


def load_stub_module(module_name: str) -> ModuleType:
    stub_path = stub_file_for(module_name)
    source = stub_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(stub_path), type_comments=True)
    module = ModuleType(f"_circuitpython_stub_{module_name}")
    for node in tree.body:
        add_stub_node(module.__dict__, node)
    return module


def stub_file_for(module_name: str) -> Path:
    for site_packages in site_package_roots():
        stub_path = site_packages / f"{module_name}-stubs" / "__init__.pyi"
        if stub_path.exists():
            return stub_path

    try:
        dist = importlib.metadata.distribution("circuitpython-stubs")
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError(
            "circuitpython-stubs is not installed. Run "
            "`UV_CACHE_DIR=.uv-cache uv add --dev circuitpython-stubs` "
            "or install it into the active test environment."
        ) from exc

    files = list(dist.files or [])
    wanted = module_name.replace(".", "/")
    candidates = {f"{wanted}.pyi", f"{wanted}/__init__.pyi"}
    for file in files:
        as_posix = file.as_posix()
        if as_posix in candidates:
            return Path(dist.locate_file(file))
    raise FileNotFoundError(f"no CircuitPython stub file found for module {module_name!r}")


def site_package_roots() -> list[Path]:
    roots: list[Path] = []
    for paths in (sysconfig.get_paths(), sysconfig.get_paths(vars=venv_vars(ROOT / ".venv"))):
        for key in ("purelib", "platlib"):
            path = Path(paths[key])
            if path not in roots:
                roots.append(path)
    return roots


def venv_vars(venv: Path) -> dict[str, str]:
    return {"base": str(venv), "platbase": str(venv)}


def add_stub_node(namespace: dict[str, Any], node: ast.AST) -> None:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if not is_public(node.name):
            return
        func = namespace.get(node.name)
        if not isinstance(func, StubFunction):
            func = StubFunction()
            namespace[node.name] = func
        func.add_signature(signature_from_args(node.args))
        return
    if isinstance(node, ast.ClassDef):
        if not is_public(node.name):
            return
        namespace[node.name] = build_stub_class(node)
        return
    for name in assigned_public_names(node):
        namespace.setdefault(name, StubConstant())


def build_stub_class(node: ast.ClassDef) -> type:
    namespace: dict[str, Any] = {"__module__": "_circuitpython_stub"}
    properties: set[str] = set()
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not is_public(child.name):
                continue
            if has_decorator(child, "property"):
                namespace[child.name] = property(StubFunction([signature_from_args(child.args)]))
                properties.add(child.name)
                continue
            if is_property_setter(child):
                properties.add(child.name)
                namespace.setdefault(child.name, property(StubFunction([signature_from_args(child.args)])))
                continue
            func = namespace.get(child.name)
            if not isinstance(func, StubFunction):
                func = StubFunction()
                namespace[child.name] = func
            func.add_signature(signature_from_args(child.args))
            continue
        for name, kind in assigned_public_class_names(child, node.name):
            if name in properties:
                continue
            if kind == "property":
                namespace.setdefault(name, property(StubFunction()))
            else:
                namespace.setdefault(name, StubConstant())
    return type(node.name, (), namespace)


def signature_from_args(args: ast.arguments) -> inspect.Signature:
    params: list[inspect.Parameter] = []
    positional = [*args.posonlyargs, *args.args]
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)

    for index, arg in enumerate(positional):
        kind = (
            inspect.Parameter.POSITIONAL_ONLY
            if index < len(args.posonlyargs)
            else inspect.Parameter.POSITIONAL_OR_KEYWORD
        )
        params.append(parameter_from_arg(arg, kind, defaults[index]))

    if args.vararg is not None:
        params.append(parameter_from_arg(args.vararg, inspect.Parameter.VAR_POSITIONAL, None))

    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        params.append(parameter_from_arg(arg, inspect.Parameter.KEYWORD_ONLY, default))

    if args.kwarg is not None:
        params.append(parameter_from_arg(args.kwarg, inspect.Parameter.VAR_KEYWORD, None))

    return inspect.Signature(params)


def parameter_from_arg(
    arg: ast.arg,
    kind: inspect._ParameterKind,
    default_node: ast.AST | None,
) -> inspect.Parameter:
    default = inspect._empty if default_node is None else default_value(default_node)
    return inspect.Parameter(arg.arg, kind, default=default)


def default_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        if node.value is Ellipsis:
            return _DefaultExpr("...")
        return node.value
    return _DefaultExpr(ast.unparse(node))


def assigned_public_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and is_public(target.id):
                names.append(target.id)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and is_public(node.target.id):
            names.append(node.target.id)
    return names


def assigned_public_class_names(node: ast.AST, class_name: str) -> list[tuple[str, str]]:
    names: list[tuple[str, str]] = []
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and is_public(target.id):
                names.append((target.id, "constant"))
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and is_public(node.target.id):
            kind = (
                "constant"
                if node.target.id.isupper() or annotation_names_class(node.annotation, class_name)
                else "property"
            )
            names.append((node.target.id, kind))
    return names


def annotation_names_class(node: ast.AST, class_name: str) -> bool:
    if isinstance(node, ast.Name):
        return node.id == class_name
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value == class_name
    if isinstance(node, ast.Attribute):
        return node.attr == class_name
    return False


def has_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    return any(isinstance(dec, ast.Name) and dec.id == name for dec in node.decorator_list)


def is_property_setter(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for dec in node.decorator_list:
        if isinstance(dec, ast.Attribute) and dec.attr == "setter":
            return True
    return False


def is_public(name: str) -> bool:
    return not name.startswith("_") or name in DUnder_API


def public_items(module: ModuleType) -> list[tuple[str, Any]]:
    return sorted(
        (name, value)
        for name, value in vars(module).items()
        if is_public(name) and name not in {"annotations"}
    )


def public_class_items(cls: type) -> list[tuple[str, Any]]:
    return sorted(
        (name, value)
        for name, value in vars(cls).items()
        if is_public(name)
    )


def kind_of(value: Any) -> str:
    if inspect.isclass(value):
        return "class"
    if isinstance(value, property):
        return "property"
    if isinstance(value, StubFunction) or callable(value):
        return "function"
    return "constant"


def unwrap_descriptor(value: Any) -> Any:
    if isinstance(value, (staticmethod, classmethod)):
        return value.__func__
    return value


def candidate_signatures(value: Any) -> list[inspect.Signature]:
    signatures = getattr(value, "__signatures__", None)
    if signatures:
        return signatures
    return [inspect.signature(value)]


def signature_shape(signature: inspect.Signature) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (
            param.name,
            param.kind.name,
            default_repr(param.default),
        )
        for param in signature.parameters.values()
    )


def default_repr(default: Any) -> str:
    if default is inspect._empty:
        return "<required>"
    return repr(default)


def format_shape(shape: tuple[tuple[str, str, str], ...]) -> str:
    return "(" + ", ".join(f"{name}:{kind}={default}" for name, kind, default in shape) + ")"


def import_layer_module(module_name: str) -> ModuleType:
    if module_name == "board":
        return importlib.import_module("pymcu_circuitpython.boards.arduino_uno")
    return importlib.import_module(f"pymcu_circuitpython.{module_name}")


def load_allowlist() -> dict[str, dict[str, str]]:
    if not ALLOWLIST_PATH.exists():
        return {}
    data = tomllib.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
    entries = data.get("deviation", [])
    docs_text = normalized_docs_text()
    allowlist: dict[str, dict[str, str]] = {}
    for entry in entries:
        symbol = entry["symbol"]
        quote = entry["quote"]
        if normalize_text(quote) not in docs_text:
            raise ValueError(f"{symbol}: allowlist quote is not present in README.md or docs/")
        allowlist[symbol] = entry
    return allowlist


def normalized_docs_text() -> str:
    chunks: list[str] = []
    for path in DOC_PATHS:
        if path.is_file() and path.suffix in {"", ".md", ".rst", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    return normalize_text("\n".join(chunks))


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def case_report(case: Case) -> tuple[str, str, str]:
    allowlist = load_allowlist()
    result = check_case(case)
    allowed = case.full_symbol in allowlist
    if result.ok and allowed:
        return case.full_symbol, "stale allowlist", "matches the stub now"
    if result.ok:
        return case.full_symbol, "provided", ""
    if allowed:
        return case.full_symbol, "allowlisted", allowlist[case.full_symbol]["reason"]
    return case.full_symbol, result.category, result.detail
