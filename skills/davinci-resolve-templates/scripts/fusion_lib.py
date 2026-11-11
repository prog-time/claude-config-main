"""Builder for DaVinci Resolve / Fusion macro (.setting) files.

Coordinates: helpers take pixel values in a reference frame (default 1920x1080,
Y from the top) and convert them to Fusion's normalized space
(Center: 0..1, Y up). Call set_frame(1080, 1920) for vertical video.

Status of every node/feature (verified in Resolve or not) is tracked in
references/verified.md. Factories marked UNVERIFIED must be checked with
make_test_pack.py before they are used in a user template.
"""

import os
import re
import shutil
import subprocess
import tempfile

FRAME_W, FRAME_H = 1920, 1080

# RectangleMask Width/Height unit. Fusion masks measure both sides in units of
# frame WIDTH (equal values -> square). A 600x300 test with Height=px/FRAME_H
# came out "square", which matches this. Confirm with Test 5 (make_test_pack).
MASK_UNIT = "width"


def set_frame(w, h):
    global FRAME_W, FRAME_H
    FRAME_W, FRAME_H = int(w), int(h)


def frame():
    return FRAME_W, FRAME_H


def fx(px):
    return round(px / FRAME_W, 5)


def fy(py):
    return round(1 - py / FRAME_H, 5)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4))


# ---------- Lua serialization ----------

class Raw:
    def __init__(self, s):
        self.s = s


def FuID(s):
    return Raw("FuID { %s }" % lua_str(s))


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def lua_val(v):
    if isinstance(v, Raw):
        return v.s
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(round(v, 6))
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return lua_str(v)
    if isinstance(v, (tuple, list)):
        return "{ " + ", ".join(lua_val(x) for x in v) + " }"
    raise TypeError(v)


class Inp:
    """An Input: constant value, expression, or link to another tool's output."""

    def __init__(self, value=None, expr=None, src=None, src_out="Output"):
        self.value, self.expr, self.src, self.src_out = value, expr, src, src_out

    def render(self):
        parts = []
        if self.src:
            parts += ["SourceOp = %s" % lua_str(self.src), "Source = %s" % lua_str(self.src_out)]
        if self.value is not None:
            parts.append("Value = %s" % lua_val(self.value))
        if self.expr:
            parts.append("Expression = %s" % lua_str(self.expr))
        return "Input { %s, }" % ", ".join(parts)


class Tool:
    def __init__(self, name, kind, pos=(0, 0)):
        self.name, self.kind, self.pos = name, kind, pos
        self.inputs = {}
        self.user_controls = []  # (id, dict)

    def set(self, key, value=None, expr=None):
        self.inputs[key] = Inp(value=value, expr=expr)
        return self

    def link(self, key, src, src_out="Output"):
        self.inputs[key] = Inp(src=src, src_out=src_out)
        return self

    def color(self, prefix, hexcol, alpha=1.0, suffix=""):
        r, g, b = hex_rgb(hexcol)
        for ch, v in (("Red", r), ("Green", g), ("Blue", b), ("Alpha", alpha)):
            self.set(f"{prefix}{ch}{suffix}", v)
        return self

    def follow_color(self, master, prefix="", suffix="1", channels=("Red", "Green", "Blue")):
        """Make this tool's color channels follow the master tool (expression link)."""
        for ch in channels:
            key = f"{prefix}{ch}{suffix}"
            cur = self.inputs.get(key)
            self.set(key, cur.value if cur else None, expr=f"{master}.{key}")
        return self

    def user_control(self, cid, **spec):
        self.user_controls.append((cid, spec))
        return self

    def render(self, ind="\t\t\t\t"):
        out = [f"{ind}{self.name} = {self.kind} {{", f"{ind}\tCtrlWZoom = false,", f"{ind}\tInputs = {{"]
        for k, v in self.inputs.items():
            key = k if k.isidentifier() else f'["{k}"]'
            out.append(f"{ind}\t\t{key} = {v.render()},")
        out.append(f"{ind}\t}},")
        out.append(f"{ind}\tViewInfo = OperatorInfo {{ Pos = {{ {self.pos[0]}, {self.pos[1]} }} }},")
        if self.user_controls:
            out.append(f"{ind}\tUserControls = ordered() {{")
            for cid, spec in self.user_controls:
                body = ", ".join(f"{k} = {lua_val(v)}" for k, v in spec.items())
                out.append(f"{ind}\t\t{cid} = {{ {body} }},")
            out.append(f"{ind}\t}},")
        out.append(f"{ind}}},")
        return "\n".join(out)

    def refs(self):
        """Names of tools this tool depends on (links + expression references)."""
        names = set()
        for inp in self.inputs.values():
            if inp.src:
                names.add(inp.src)
            if inp.expr:
                names.update(re.findall(r"(?<![\w.])([A-Za-z_]\w*)\s*\.", inp.expr))
        return names


class Spline:
    """BezierSpline animating one Number input. UNVERIFIED in Resolve (Test 8).

    keys: list of (frame, value). ease=True gives flat handles (ease in/out).
    """
    kind = "BezierSpline"

    def __init__(self, name, keys, ease=True):
        self.name, self.keys, self.ease = name, sorted(keys), ease
        self.pos = (0, 0)
        self.inputs, self.user_controls = {}, []

    def render(self, ind="\t\t\t\t"):
        rows = []
        for i, (f, v) in enumerate(self.keys):
            parts = [lua_val(float(v))]
            if i > 0:
                pf, pv = self.keys[i - 1]
                lv = v if self.ease else v - (v - pv) / 3
                parts.append(f"LH = {{ {round(f - (f - pf) / 3, 4)}, {round(lv, 6)} }}")
            if i < len(self.keys) - 1:
                nf, nv = self.keys[i + 1]
                rv = v if self.ease else v + (nv - v) / 3
                parts.append(f"RH = {{ {round(f + (nf - f) / 3, 4)}, {round(rv, 6)} }}")
            if not self.ease:
                parts.append("Flags = { Linear = true }")
            rows.append(f"{ind}\t\t[{f}] = {{ {', '.join(parts)} }},")
        return "\n".join([f"{ind}{self.name} = BezierSpline {{",
                          f"{ind}\tSplineColor = {{ Red = 205, Green = 205, Blue = 16 }},",
                          f"{ind}\tNameSet = true,",
                          f"{ind}\tKeyFrames = {{", *rows, f"{ind}\t}}", f"{ind}}},"])

    def refs(self):
        return set()


class XYPath(Tool):
    """XYPath animating a Point input from two splines. UNVERIFIED (Test 8)."""

    def __init__(self, name, x_spline, y_spline):
        super().__init__(name, "XYPath")
        self.link("X", x_spline, "Value").link("Y", y_spline, "Value")

    def render(self, ind="\t\t\t\t"):
        out = [f"{ind}{self.name} = XYPath {{", f"{ind}\tShowKeyPoints = false,",
               f"{ind}\tDrawMode = \"ModifyOnly\",", f"{ind}\tCtrlWZoom = false,", f"{ind}\tInputs = {{"]
        for k, v in self.inputs.items():
            out.append(f"{ind}\t\t{k} = {v.render()},")
        out += [f"{ind}\t}},", f"{ind}}},"]
        return "\n".join(out)


def animate_number(tool, key, keys, ease=True):
    """Keyframe tool.inputs[key]; returns the Spline to add to the tool list."""
    sp = Spline(f"{tool.name}{key.replace('.', '')}", keys, ease)
    tool.link(key, sp.name, "Value")
    return sp


def animate_point(tool, key, keys, ease=True):
    """keys: list of (frame, (x, y)) in normalized coords. Returns [splineX, splineY, path]."""
    base = f"{tool.name}{key}"
    sx = Spline(base + "X", [(f, p[0]) for f, p in keys], ease)
    sy = Spline(base + "Y", [(f, p[1]) for f, p in keys], ease)
    path = XYPath(base + "Path", sx.name, sy.name)
    tool.link(key, path.name, "Value")
    return [sx, sy, path]


# ---------- node factories (verified) ----------

def _frame(t):
    t.set("Width", FRAME_W).set("Height", FRAME_H).set("UseFrameFormatSettings", 1)
    t.set("Gamut.SLogVersion", FuID("SLog2"))
    return t


def background(name, hexcol, alpha=1.0, bottom_hex=None, mask=None, pos=(0, 0)):
    t = _frame(Tool(name, "Background", pos))
    if bottom_hex:
        t.set("Type", FuID("Vertical"))
        t.color("TopLeft", hexcol, alpha)
        t.color("BottomLeft", bottom_hex, alpha)
    else:
        t.color("TopLeft", hexcol, alpha)
    if mask:
        t.link("EffectMask", mask, "Mask")
    return t


def rect_mask(name, cx, cy, w, h, radius=0.0, soft=0.0, unit=None, pos=(0, 0)):
    """cx, cy, w, h in reference-frame pixels (Y from top).

    radius: CornerRadius 0..1 (fraction of the shorter half-side).
    soft: SoftEdge (UNVERIFIED, used for shadows).
    unit: override MASK_UNIT ("width" | "height") — only for diagnostics.
    """
    unit = unit or MASK_UNIT
    t = Tool(name, "RectangleMask", pos)
    t.set("Filter", FuID("Fast Gaussian"))
    t.set("MaskWidth", FRAME_W).set("MaskHeight", FRAME_H)
    t.set("PixelAspect", (1, 1)).set("UseFrameFormatSettings", 1)
    t.set("ClippingMode", FuID("None"))
    t.set("Center", (fx(cx), fy(cy)))
    t.set("Width", round(w / FRAME_W, 5))
    t.set("Height", round(h / (FRAME_W if unit == "width" else FRAME_H), 5))
    t.set("CornerRadius", radius)
    if soft:
        t.set("SoftEdge", soft)
    return t


def text(name, txt, x, y, size_px, hexcol, font="Inter", style="Regular",
         h_anchor=-1, v_anchor=-1, line_spacing=None, scale_expr=None, alpha=1.0, pos=(0, 0)):
    """x, y = anchor point in px. h_anchor: -1 left, 0 center, 1 right.
    v_anchor: -1 top, 0 center, 1 bottom. Size is relative to frame width."""
    t = _frame(Tool(name, "TextPlus", pos))
    t.set("Center", (fx(x), fy(y)))
    t.set("StyledText", txt)
    t.set("Font", font).set("Style", style)
    base = round(size_px / FRAME_W, 6)
    if scale_expr:
        t.set("Size", base, expr=f"{scale_expr}*{base}")
    else:
        t.set("Size", base)
    t.set("HorizontalLeftCenterRight", h_anchor)
    t.set("VerticalTopCenterBottom", v_anchor)
    if h_anchor == -1:
        t.set("HorizontalJustificationNew", 0)  # UNVERIFIED: left justify multi-line
    if line_spacing:
        t.set("LineSpacing", line_spacing)
    t.color("", hexcol, alpha=alpha, suffix="1")
    return t


def merge(name, bg, fg, blend=1.0, pos=(0, 0)):
    t = Tool(name, "Merge", pos)
    t.link("Background", bg).link("Foreground", fg)
    t.set("PerformDepthMerge", 0)
    t.set("Blend", blend)
    return t


def transform(name, src, center=(0.5, 0.5), size=1.0, pos=(0, 0)):
    t = Tool(name, "Transform", pos)
    t.link("Input", src)
    t.set("Center", center).set("Size", size)
    return t


# ---------- node factories (UNVERIFIED — see references/verified.md) ----------

def shadow(prefix, cx, cy, w, h, radius=0.0, hexcol="#000000", alpha=0.45,
           offset=(0, 12), soft=0.02):
    """Soft rectangular shadow from verified primitives (mask + Background).
    Returns [mask, background]; merge the background UNDER the element."""
    m = rect_mask(f"{prefix}Mask", cx + offset[0], cy + offset[1], w, h, radius, soft=soft)
    return [m, background(prefix, hexcol, alpha=alpha, mask=m.name)]


def blur(name, src, size=10.0):
    t = Tool(name, "Blur")
    t.link("Input", src)
    t.set("XBlurSize", size)
    return t


def soft_glow(name, src, threshold=0.2, gain=1.0, size=10.0):
    t = Tool(name, "SoftGlow")
    t.link("Input", src)
    t.set("Threshold", threshold).set("Gain", gain).set("XGlowSize", size)
    return t


def _shape_xy(cx, cy):
    # shape space: origin at frame center, units of frame width, Y up
    return round((cx - FRAME_W / 2) / FRAME_W, 5), round((FRAME_H / 2 - cy) / FRAME_W, 5)


def s_rectangle(name, cx, cy, w, h, hexcol, radius=0.0, alpha=1.0):
    t = Tool(name, "sRectangle")
    x, y = _shape_xy(cx, cy)
    t.set("Translate.X", x).set("Translate.Y", y)
    t.set("Width", round(w / FRAME_W, 5)).set("Height", round(h / FRAME_W, 5))
    t.set("CornerRadius", radius)
    t.color("", hexcol, alpha)
    return t


def s_ellipse(name, cx, cy, w, h, hexcol, alpha=1.0):
    t = Tool(name, "sEllipse")
    x, y = _shape_xy(cx, cy)
    t.set("Translate.X", x).set("Translate.Y", y)
    t.set("Width", round(w / FRAME_W, 5)).set("Height", round(h / FRAME_W, 5))
    t.color("", hexcol, alpha)
    return t


def s_merge(name, inputs):
    t = Tool(name, "sMerge")
    for i, src in enumerate(inputs, 1):
        t.link(f"Input{i}", src)
    return t


def s_render(name, src):
    t = _frame(Tool(name, "sRender"))
    t.link("Input", src)
    return t


# ---------- animation ----------

def add_anim_controls(xf, frames=12, slide=0.04):
    """User controls on the master Transform: AnimOn, AnimFrames, SlideDist."""
    xf.set("AnimOn", 1).set("AnimFrames", frames).set("SlideDist", slide)
    xf.user_control("AnimOn", LINKS_Name="Animation", LINKID_DataType="Number",
                    INPID_InputControl="CheckboxControl", INP_Integer=False, INP_Default=1,
                    CBC_TriState=False, ICS_ControlPage="Controls")
    xf.user_control("AnimFrames", LINKS_Name="Anim Frames", LINKID_DataType="Number",
                    INPID_InputControl="SliderControl", INP_Integer=True, INP_Default=frames,
                    INP_MinScale=1, INP_MaxScale=60, INP_MinAllowed=1, ICS_ControlPage="Controls")
    xf.user_control("SlideDist", LINKS_Name="Slide Distance", LINKID_DataType="Number",
                    INPID_InputControl="SliderControl", INP_Default=slide, INP_MinScale=0.0,
                    INP_MaxScale=0.3, ICS_ControlPage="Controls")
    return xf


def animation(src, ctrl, mode="expr", frames=12, slide=0.04, outro=True, prefix=""):
    """Wrap `src` with intro/outro and a transparent canvas.

    mode:
      "expr"   — expressions driven by ctrl.AnimOn/AnimFrames/SlideDist
                 (needs add_anim_controls(ctrl)); intro + optional outro. UNVERIFIED.
      "keys"   — keyframes (BezierSpline/XYPath), intro only. UNVERIFIED.
      "static" — no animation (bisection / safe fallback).
    Returns (tools, output_name). Output node is f"{prefix}MrgOut".
    """
    tools = []
    xf = transform(f"{prefix}XfAnim", src)
    canvas = background(f"{prefix}BgCanvas", "#000000", alpha=0.0)
    out = merge(f"{prefix}MrgOut", canvas.name, xf.name)
    if mode == "expr":
        p_in = f"min(1, max(0, time/{ctrl}.AnimFrames))"
        p_out = f"min(1, max(0, (comp.RenderEnd - time)/{ctrl}.AnimFrames))"
        p = f"min({p_in}, {p_out})" if outro else p_in
        p = f"iif({ctrl}.AnimOn > 0.5, {p}, 1)"
        q = f"(1-{p})"
        xf.set("Center", (0.5, 0.5), expr=f"Point(0.5, 0.5 - {ctrl}.SlideDist*{q}*{q}*{q})")
        out.set("Blend", 1.0, expr=p)
        tools += [xf, canvas, out]
    elif mode == "keys":
        tools += animate_point(xf, "Center", [(0, (0.5, 0.5 - slide)), (frames, (0.5, 0.5))])
        tools.append(animate_number(out, "Blend", [(0, 0.0), (frames, 1.0)]))
        tools += [xf, canvas, out]
    elif mode == "static":
        tools += [xf, canvas, out]
    else:
        raise ValueError(f"unknown animation mode {mode!r}")
    return tools, out.name


# ---------- macro ----------

class Publish:
    def __init__(self, op, source, name=None, group=None, default=None):
        self.op, self.source, self.name, self.group, self.default = op, source, name, group, default


def publish_color(op, prefix, name, group, suffix=""):
    return [Publish(op, f"{prefix}Red{suffix}", name, group),
            Publish(op, f"{prefix}Green{suffix}", None, group),
            Publish(op, f"{prefix}Blue{suffix}", None, group),
            Publish(op, f"{prefix}Alpha{suffix}", None, group)]


def publish_font(op, name, group):
    """Font + Style in one ControlGroup (UNVERIFIED that Resolve groups them)."""
    return [Publish(op, "Font", name, group), Publish(op, "Style", None, group)]


RESERVED = {
    # Lua keywords
    "and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto", "if",
    "in", "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while",
    # .setting / expression words
    "Name", "Input", "Output", "Inputs", "Outputs", "Value", "Source", "SourceOp", "Tools",
    "Expression", "Text", "Point", "comp", "time", "self", "tool", "fusion", "app", "math",
    "iif", "min", "max", "abs", "floor", "ceil", "Width", "Height", "Center", "Size",
    # tool kinds
    "Background", "Merge", "Transform", "TextPlus", "RectangleMask", "EllipseMask", "Blur",
    "SoftGlow", "Loader", "MediaIn", "MediaOut", "sRectangle", "sEllipse", "sMerge", "sRender",
    "BezierSpline", "XYPath", "MacroOperator", "GroupOperator",
}
EXPR_GLOBALS = {"comp", "self", "math", "tool", "fusion", "app"}
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def check_names(name, tools, publishes, output_tool, main_input=None):
    """Unique, safe node names; every link/expression/publish points to a real node."""
    errs = []
    names = [t.name for t in tools]
    seen = set()
    for n in [name] + names:
        if not NAME_RE.match(n):
            errs.append(f"bad node name {n!r} (letters, digits, _ only)")
        if n in RESERVED:
            errs.append(f"reserved node name {n!r} — use a prefix, e.g. Txt{n} / Xf{n}")
        if n in seen:
            errs.append(f"duplicate node name {n!r}")
        seen.add(n)
    known = set(names)
    for t in tools:
        for r in t.refs() - EXPR_GLOBALS:
            if r not in known:
                errs.append(f"{t.name}: references unknown node {r!r}")
    for p in publishes:
        if p.op not in known:
            errs.append(f"publish {p.source!r}: unknown node {p.op!r}")
    if output_tool not in known:
        errs.append(f"output node {output_tool!r} not found")
    if main_input and main_input[0] not in known:
        errs.append(f"main input node {main_input[0]!r} not found")
    if errs:
        raise ValueError("node check failed:\n  " + "\n  ".join(errs))


def macro(name, tools, publishes, output_tool, main_input=None):
    """Render a MacroOperator. main_input=(tool, input) adds MainInput1 (Effects)."""
    check_names(name, tools, publishes, output_tool, main_input)
    lines = ["{", "\tTools = ordered() {", f"\t\t{name} = MacroOperator {{",
             "\t\t\tCtrlWZoom = false,", "\t\t\tNameSet = true,", "\t\t\tInputs = ordered() {"]
    if main_input:
        lines.append(f"\t\t\t\tMainInput1 = InstanceInput {{ SourceOp = {lua_str(main_input[0])}, "
                     f"Source = {lua_str(main_input[1])}, }},")
    for i, p in enumerate(publishes, 1):
        parts = [f"SourceOp = {lua_str(p.op)}", f"Source = {lua_str(p.source)}"]
        if p.name:
            parts.append(f"Name = {lua_str(p.name)}")
        if p.group is not None:
            parts.append(f"ControlGroup = {p.group}")
        if p.default is not None:
            parts.append(f"Default = {lua_val(p.default)}")
        lines.append(f"\t\t\t\tInput{i} = InstanceInput {{ {', '.join(parts)}, }},")
    lines += ["\t\t\t},", "\t\t\tOutputs = {",
              f"\t\t\t\tMainOutput1 = InstanceOutput {{ SourceOp = {lua_str(output_tool)}, Source = \"Output\", }},",
              "\t\t\t},",
              "\t\t\tViewInfo = GroupInfo { Pos = { 0, 0 } },",
              "\t\t\tTools = ordered() {"]
    for t in tools:
        lines.append(t.render())
    lines += ["\t\t\t},", "\t\t},", "\t},", f"\tActiveTool = {lua_str(name)}", "}", ""]
    return "\n".join(lines)


def layout(tools, step=110):
    """Spread nodes left to right in the Fusion flow view."""
    for i, t in enumerate(tools):
        t.pos = (i * step, 0)
    return tools


# ---------- validation ----------

def validate(src):
    """Structural check: balanced braces/parens outside strings, closed strings.
    Also runs `luac -p` when luac is installed."""
    stack, i, n = [], 0, len(src)
    pairs = {"}": "{", ")": "(", "]": "["}
    while i < n:
        c = src[i]
        if c == '"':
            i += 1
            while i < n and src[i] != '"':
                if src[i] == "\\":
                    i += 1
                if i < n and src[i] == "\n":
                    raise ValueError(f"newline inside string at {i}")
                i += 1
            if i >= n:
                raise ValueError("unterminated string")
        elif c in "{([":
            stack.append((c, i))
        elif c in "})]":
            if not stack or stack[-1][0] != pairs[c]:
                raise ValueError(f"unbalanced {c} at {i}: ...{src[max(0, i - 80):i + 1]}")
            stack.pop()
        i += 1
    if stack:
        raise ValueError(f"unclosed {stack[-1]}")
    luac_check(src)
    return True


def luac_check(src):
    """`luac -p` on 'return <src>'. Returns True/False/None (None = luac missing)."""
    luac = shutil.which("luac") or shutil.which("luac5.4") or shutil.which("luac5.1")
    if not luac:
        return None
    fd, path = tempfile.mkstemp(suffix=".lua")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("return " + src)
        r = subprocess.run([luac, "-p", path], capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError("luac: " + (r.stderr or r.stdout).strip())
        return True
    finally:
        os.unlink(path)


# ---------- preview PNG (optional, needs Pillow) ----------

FONT_DIRS = [os.path.expanduser("~/Library/Fonts"), "/Library/Fonts", "/System/Library/Fonts",
             "/System/Library/Fonts/Supplemental", os.path.expanduser("~/.local/share/fonts"),
             "/usr/share/fonts", os.path.expandvars(r"%WINDIR%\Fonts")]


def _find_font(family, style):
    want = [f"{family}-{style}".lower().replace(" ", ""), f"{family}{style}".lower().replace(" ", ""),
            family.lower().replace(" ", "")]
    for d in FONT_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for fn in files:
                stem = os.path.splitext(fn)[0].lower().replace(" ", "")
                if fn.lower().endswith((".ttf", ".otf", ".ttc")) and any(stem.startswith(w) for w in want):
                    return os.path.join(root, fn)
    return None


def render_preview(tools, path, width=400):
    """Approximate thumbnail from the node list (masks+backgrounds, Text+).
    Expressions are ignored; merges with Blend 0 hide their foreground.
    Returns path or None when Pillow is not installed."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    W, H = FRAME_W, FRAME_H
    img = Image.new("RGBA", (W, H), (24, 24, 24, 255))
    by = {t.name: t for t in tools}
    hidden = set()
    for t in tools:
        if t.kind == "Merge" and t.inputs.get("Blend") and t.inputs["Blend"].value == 0 \
                and not t.inputs["Blend"].expr and t.inputs.get("Foreground"):
            todo = [t.inputs["Foreground"].src]
            while todo:
                n = todo.pop()
                hidden.add(n)
                tn = by.get(n)
                if tn and tn.kind == "Merge":
                    todo += [tn.inputs[k].src for k in ("Background", "Foreground") if k in tn.inputs]

    def v(t, k, d=None):
        return t.inputs[k].value if k in t.inputs and t.inputs[k].value is not None else d

    def rgba(t, prefix, suffix=""):
        return tuple(int(255 * v(t, f"{prefix}{c}{suffix}", 1.0)) for c in ("Red", "Green", "Blue", "Alpha"))

    for t in tools:
        if t.name in hidden:
            continue
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if t.kind == "Background":
            col = rgba(t, "TopLeft")
            if col[3] == 0:
                continue
            m = by.get(t.inputs["EffectMask"].src) if "EffectMask" in t.inputs else None
            box = [0, 0, W, H]
            if m:
                cx, cy = v(m, "Center")
                mw = v(m, "Width") * W
                mh = v(m, "Height") * (W if MASK_UNIT == "width" else H)
                x0, y0 = cx * W - mw / 2, (1 - cy) * H - mh / 2
                box = [x0, y0, x0 + mw, y0 + mh]
                r = v(m, "CornerRadius", 0) * min(mw, mh) / 2
                d.rounded_rectangle(box, radius=r, fill=col)
            else:
                d.rectangle(box, fill=col)
            if "BottomLeftRed" in t.inputs:  # vertical gradient inside the shape
                bot = rgba(t, "BottomLeft")
                y0, y1 = int(box[1]), max(int(box[1]) + 1, int(box[3]))
                grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                gd = ImageDraw.Draw(grad)
                for y in range(max(0, y0), min(H, y1)):
                    k = (y - y0) / (y1 - y0)
                    gd.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(col, bot)))
                layer = Image.composite(grad, layer, layer.split()[3])
        elif t.kind == "TextPlus":
            txt = v(t, "StyledText", "")
            if not txt:
                continue
            size = max(4, int(v(t, "Size", 0.05) * W))
            fp = _find_font(v(t, "Font", "Inter"), v(t, "Style", "Regular"))
            try:
                font = ImageFont.truetype(fp, size) if fp else ImageFont.load_default(size)
            except Exception:
                font = ImageFont.load_default()
            cx, cy = v(t, "Center", (0.5, 0.5))
            ha = {-1: "l", 0: "m", 1: "r"}[v(t, "HorizontalLeftCenterRight", 0)]
            va = {-1: "a", 0: "m", 1: "d"}[v(t, "VerticalTopCenterBottom", 0)]
            d.multiline_text((cx * W, (1 - cy) * H), txt, font=font, fill=rgba(t, "", "1"),
                             anchor=ha + va, align={"l": "left", "m": "center", "r": "right"}[ha])
        else:
            continue
        img = Image.alpha_composite(img, layer)
    img = img.convert("RGB")
    img.thumbnail((width, width))
    img.save(path)
    return path
