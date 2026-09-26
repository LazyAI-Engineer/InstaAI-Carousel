from pathlib import Path
import html
from playwright.sync_api import sync_playwright

WIDTH = 1080
HEIGHT = 1350

# ============================================================
# LAZY AI ENGINEER — ADAPTIVE CAROUSEL RENDERER
# 1080 x 1350 | HTML/CSS layout + SVG visual engine
# ============================================================

def e(value):
    return html.escape(str(value or ""))

def clean_list(value, limit=4):
    if not isinstance(value, list):
        return []
    return [str(x)[:110] for x in value[:limit]]

def clamp_text(value, limit):
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit - 1].rsplit(" ", 1)[0]
    return (cut or text[:limit - 1]) + "…"

def headline_class(text):
    n = len(str(text or ""))
    if n <= 22: return "headline xl"
    if n <= 36: return "headline lg"
    if n <= 52: return "headline md"
    return "headline sm"

def body_class(text):
    n = len(str(text or ""))
    if n <= 125: return "bodycopy lg"
    if n <= 210: return "bodycopy md"
    return "bodycopy sm"

def fit_label(text, max_len=24):
    return clamp_text(text, max_len)

def svg_defs():
    return """
    <defs>
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#dffaff"/>
        <stop offset="25%" stop-color="#7196a6"/>
        <stop offset="58%" stop-color="#274554"/>
        <stop offset="100%" stop-color="#0a1720"/>
      </linearGradient>
      <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#103449" stop-opacity=".95"/>
        <stop offset="100%" stop-color="#06131f" stop-opacity=".78"/>
      </linearGradient>
      <radialGradient id="core">
        <stop offset="0%" stop-color="#48f5ff"/>
        <stop offset="32%" stop-color="#0aaed1"/>
        <stop offset="72%" stop-color="#0a4058"/>
        <stop offset="100%" stop-color="#071924"/>
      </radialGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="6" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="shadow">
        <feDropShadow dx="0" dy="16" stdDeviation="14" flood-color="#000" flood-opacity=".5"/>
      </filter>
    </defs>
    """

def svg_text(x, y, text, size=18, anchor="middle", weight=700, color="#dffaff", spacing=0):
    label = e(fit_label(text, 30))
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" letter-spacing="{spacing}">{label}</text>'


def svg_wrap(x, y, w, h, text, size=16, weight=700, color="#dffaff",
             align="center", max_chars=80, line_height=1.18):
    """HTML text inside SVG: real wrapping + clipping + centered vertical layout."""
    label = e(clamp_text(text, max_chars))
    justify = {"start":"flex-start","end":"flex-end"}.get(align, "center")
    text_align = {"start":"left","end":"right"}.get(align, "center")
    return f"""
    <foreignObject x="{x}" y="{y}" width="{w}" height="{h}">
      <div xmlns="http://www.w3.org/1999/xhtml"
           style="width:100%;height:100%;display:flex;align-items:center;justify-content:{justify};
                  overflow:hidden;padding:4px 8px;font-family:Arial,sans-serif;font-size:{size}px;
                  line-height:{line_height};font-weight:{weight};color:{color};text-align:{text_align};
                  overflow-wrap:anywhere;word-break:normal;">
        {label}
      </div>
    </foreignObject>
    """

def core(cx=540, cy=305, r=88, label="AI"):
    return f"""
    <circle cx="{cx}" cy="{cy}" r="{r+38}" fill="#00eaff" opacity=".055"/>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="#061824" stroke="#00eaff" stroke-width="2"/>
    <circle cx="{cx}" cy="{cy}" r="{r-18}" fill="url(#core)" stroke="#63f5ff" stroke-opacity=".55"/>
    <ellipse cx="{cx}" cy="{cy}" rx="{r+40}" ry="31" fill="none" stroke="#00eaff" stroke-opacity=".22"/>
    <ellipse cx="{cx}" cy="{cy}" rx="31" ry="{r+40}" fill="none" stroke="#00eaff" stroke-opacity=".15"/>
    {svg_text(cx, cy+10, label, 31, "middle", 800, "#ffffff")}
    """

def panel(x, y, w, h, title="", body=""):
    return f"""
    <g filter="url(#shadow)">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="25" fill="url(#glass)" stroke="#00dfff" stroke-opacity=".48"/>
      {svg_text(x+w/2, y+42, title, 18, "middle", 800, "#c8f8ff", 1)}
      {svg_text(x+w/2, y+78, body, 14, "middle", 500, "#7fb2c5")}
    </g>
    """

def hero_scene(d, visual):
    # Generic goal -> AI -> action; becomes RAG-specific when content indicates RAG.
    raw = (str(visual) + " " + str(d)).lower()
    if any(k in raw for k in ("rag", "retriev", "vector", "knowledge")):
        return f"""
        <ellipse cx="540" cy="310" rx="450" ry="245" fill="#00dfff" opacity=".04"/>
        {panel(70,225,245,165,"SOURCE KNOWLEDGE","documents • facts")}
        <path d="M315 308 C380 308 400 308 438 308" stroke="#00eaff" stroke-width="3" fill="none"/>
        <circle cx="370" cy="308" r="5" fill="#00eaff" filter="url(#glow)"/>
        {core(540,308,92,"AI")}
        <path d="M642 308 C690 308 710 300 730 280" stroke="#00eaff" stroke-width="3" fill="none"/>
        <g filter="url(#shadow)">
          <ellipse cx="840" cy="225" rx="105" ry="27" fill="#123c4d" stroke="#00eaff"/>
          <path d="M735 225 v145 c0 38 210 38 210 0 V225" fill="url(#glass)" stroke="#00dfff"/>
          <ellipse cx="840" cy="275" rx="105" ry="27" fill="#0a2938" stroke="#16718a"/>
          <ellipse cx="840" cy="325" rx="105" ry="27" fill="#0a2938" stroke="#16718a"/>
          <ellipse cx="840" cy="370" rx="105" ry="27" fill="#09212f" stroke="#00dfff"/>
          {svg_text(840,420,"VECTOR STORE",17,"middle",800,"#bff8ff",2)}
        </g>
        <path d="M610 385 C665 430 715 455 760 468" stroke="#00eaff" stroke-width="3" fill="none"/>
        {panel(760,430,240,105,"GROUNDED ANSWER","current • relevant")}
        {svg_text(195,430,"RETRIEVE",14,"middle",800,"#00eaff",3)}
        {svg_text(540,458,"AUGMENT",14,"middle",800,"#00eaff",3)}
        {svg_text(870,560,"GENERATE",14,"middle",800,"#00eaff",3)}
        """
    left = d.get("left", "Goal")
    center = d.get("center", "AI Agent")
    right = d.get("right", "Action")
    return f"""
    {panel(80,250,230,125,left,"input")}
    <path d="M310 312 H430" stroke="#00eaff" stroke-width="3"/>
    {core(540,312,92,center)}
    <path d="M650 312 H770" stroke="#00eaff" stroke-width="3"/>
    {panel(770,250,230,125,right,"output")}
    """

def comparison_scene(d):
    lt = d.get("left_title","Option A")
    rt = d.get("right_title","Option B")
    left = clean_list(d.get("left_items",[]),4)
    right = clean_list(d.get("right_items",[]),4)

    def items(x, arr):
        out=""
        for i,item in enumerate(arr):
            y=205+i*78
            out += f'<circle cx="{x+12}" cy="{y+26}" r="5" fill="#00eaff"/>'
            out += svg_wrap(x+32,y,350,52,item,16,600,"#b8d9e6","start",62)
        return out

    return f"""
    <rect x="55" y="95" width="455" height="470" rx="30" fill="url(#glass)" stroke="#176278"/>
    <rect x="570" y="95" width="455" height="470" rx="30" fill="url(#glass)" stroke="#00dfff" stroke-opacity=".65"/>
    {svg_wrap(88,125,385,58,lt,25,800,"#dffaff","start",36)}
    {svg_wrap(603,125,385,58,rt,25,800,"#dffaff","start",36)}
    {items(82,left)}
    {items(597,right)}
    """

def flow_scene(d):
    steps = clean_list(d.get("steps",[]),5) or ["Perceive","Plan","Act","Check"]
    n=len(steps)
    margin=45
    gap=18
    w=(1080-2*margin-gap*(n-1))/n
    out=""
    for i,label in enumerate(steps):
        x=margin+i*(w+gap)
        cx=x+w/2
        out += f"""
        <rect x="{x}" y="220" width="{w}" height="180" rx="28"
              fill="url(#glass)" stroke="#00dfff" stroke-opacity=".68"/>
        <circle cx="{cx}" cy="270" r="24" fill="#00eaff" opacity=".12"/>
        {svg_text(cx,278,str(i+1),20,"middle",800,"#00eaff")}
        {svg_wrap(x+12,305,w-24,78,label,15,800,"#dffaff","center",42)}
        """
        if i<n-1:
            nx=margin+(i+1)*(w+gap)
            out += f'<path d="M{x+w} 310 H{nx}" stroke="#00eaff" stroke-width="3" stroke-opacity=".55"/>'
    return out

def tools_scene(d):
    tools = clean_list(d.get("tools",[]),4) or ["Browser","Code","Calculator","Calendar"]
    coords=[(220,190),(860,190),(220,440),(860,440)]
    out=core(540,315,80,"AI")
    for (x,y),tool in zip(coords,tools):
        out += f"""
        <path d="M540 315 L{x} {y}" stroke="#00eaff" stroke-opacity=".18" stroke-width="2"/>
        <rect x="{x-115}" y="{y-58}" width="230" height="116" rx="25" fill="url(#glass)" stroke="#00dfff" stroke-opacity=".5"/>
        <circle cx="{x}" cy="{y-22}" r="16" fill="#00eaff" opacity=".13" stroke="#00eaff"/>
        {svg_wrap(x-100,y+4,200,48,tool,16,800,"#dffaff","center",32)}
        """
    return out

def cards_scene(d):
    cards = d.get("cards",[]) if isinstance(d.get("cards",[]),list) else []
    cards = cards[:4]
    coords=[(55,95),(555,95),(55,335),(555,335)]
    out=""
    for (x,y),card in zip(coords,cards):
        if not isinstance(card,dict): continue
        title=card.get("title","")
        desc=card.get("description","")
        out += f"""
        <rect x="{x}" y="{y}" width="470" height="205" rx="28" fill="url(#glass)" stroke="#16718a" stroke-opacity=".7"/>
        <circle cx="{x+42}" cy="{y+48}" r="17" fill="#00eaff" opacity=".15" stroke="#00eaff"/>
        {svg_wrap(x+75,y+20,350,58,title,21,800,"#dffaff","start",42)}
        {svg_wrap(x+25,y+88,420,86,desc,15,500,"#9fc5d4","start",105,1.28)}
        """
    return out

def equation_scene(d):
    terms=clean_list(d.get("terms",[]),3) or ["Language Model","Tools","Autonomy"]
    result=fit_label(d.get("result","AI Agent"),25)
    xs=[190,540,890]
    out=""
    for i,(x,t) in enumerate(zip(xs,terms)):
        out += f"""
        <rect x="{x-135}" y="190" width="270" height="120" rx="25" fill="url(#glass)" stroke="#00dfff" stroke-opacity=".6"/>
        {svg_text(x,260,t,19,"middle",800)}
        """
        if i<2:
            out += svg_text((x+xs[i+1])//2,265,"+",30,"middle",700,"#00eaff")
    out += f"""
    <path d="M540 335 V390" stroke="#00eaff" stroke-width="3"/>
    <rect x="335" y="390" width="410" height="125" rx="30" fill="#08364a" stroke="#00eaff" stroke-width="2"/>
    {svg_text(540,465,result,28,"middle",800,"#ffffff")}
    """
    return out

def process_scene(d):
    start=d.get("start","Goal")
    steps=clean_list(d.get("steps",[]),3) or ["Research","Analyze","Create"]
    end=d.get("end","Result")
    labels=[start]+steps+[end]
    n=len(labels)
    margin=35
    gap=14
    w=(1080-2*margin-gap*(n-1))/n
    out=""
    for i,label in enumerate(labels):
        x=margin+i*(w+gap)
        cx=x+w/2
        out += f"""
        <rect x="{x}" y="225" width="{w}" height="170" rx="28"
              fill="url(#glass)" stroke="#00dfff" stroke-opacity=".65"/>
        <circle cx="{cx}" cy="270" r="23" fill="#00eaff" opacity=".12"/>
        {svg_text(cx,278,str(i+1),19,"middle",800,"#00eaff")}
        {svg_wrap(x+10,305,w-20,72,label,14,800,"#dffaff","center",48)}
        """
        if i<n-1:
            nx=margin+(i+1)*(w+gap)
            out += f'<path d="M{x+w} 310 H{nx}" stroke="#00eaff" stroke-width="3" stroke-opacity=".5"/>'
    return out

def visual_svg(slide):
    vt=str(slide.get("visual_type","hero")).lower()
    d=slide.get("visual_data") if isinstance(slide.get("visual_data"),dict) else {}
    visual=slide.get("visual","")
    if vt=="comparison": content=comparison_scene(d)
    elif vt=="flowchart": content=flow_scene(d)
    elif vt=="tools": content=tools_scene(d)
    elif vt=="cards": content=cards_scene(d)
    elif vt=="equation": content=equation_scene(d)
    elif vt=="process": content=process_scene(d)
    else: content=hero_scene(d,visual)
    return f'<svg viewBox="0 0 1080 620" preserveAspectRatio="xMidYMid meet">{svg_defs()}{content}</svg>'

CSS = """
*{box-sizing:border-box}
html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:#050b15}
body{font-family:Inter,Arial,Helvetica,sans-serif;color:#fff}
.slide{
 position:relative;width:1080px;height:1350px;overflow:hidden;
 background:
 radial-gradient(circle at 50% 61%,rgba(0,218,255,.085),transparent 34%),
 linear-gradient(145deg,#071522 0%,#061420 50%,#050817 100%);
}
.slide:before,.slide:after{
 content:"";position:absolute;left:-8%;width:116%;height:180px;border-radius:50%;
 border-top:1px solid rgba(50,139,180,.15);pointer-events:none
}
.slide:before{top:395px}.slide:after{top:1015px}
.header{position:absolute;left:60px;right:60px;top:43px;height:32px;display:flex;align-items:center;justify-content:space-between}
.brand{font-size:20px;font-weight:800;letter-spacing:5px;color:#dff7ff;white-space:nowrap}
.brand-dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#00eaff;margin-right:20px;box-shadow:0 0 15px #00eaff}
.counter{font-size:16px;letter-spacing:4px;color:#6f99b0}
.copy{
 position:absolute;left:60px;right:60px;top:105px;height:285px;
 overflow:hidden;z-index:20
}
.headline{margin:0 0 20px;font-weight:850;line-height:1.02;letter-spacing:-1.5px;color:#f8fcff;
 overflow-wrap:anywhere}
.headline.xl{font-size:64px}.headline.lg{font-size:58px}.headline.md{font-size:50px}.headline.sm{font-size:43px}
.bodycopy{margin:0;color:#b9d8eb;font-weight:400;max-width:970px;overflow-wrap:anywhere}
.bodycopy.lg{font-size:31px;line-height:1.28}.bodycopy.md{font-size:28px;line-height:1.31}.bodycopy.sm{font-size:25px;line-height:1.32}
.visual{
 position:absolute;left:0;right:0;top:430px;height:650px;overflow:hidden;z-index:10
}
.visual svg{display:block;width:100%;height:100%;overflow:hidden}
.footer-center{
 position:absolute;left:300px;right:300px;bottom:157px;height:30px;
 display:flex;align-items:center;gap:14px;color:#6599b3;font-size:16px;letter-spacing:5px;white-space:nowrap
}
.footer-center:before,.footer-center:after{content:"";height:2px;background:#00eaff;flex:1;min-width:45px}
.footer-left,.footer-right{position:absolute;bottom:34px;font-size:12px;letter-spacing:4px;color:#4d7f98}
.footer-left{left:60px}.footer-right{right:60px}
"""

JS_AUTOFIT = r"""
function fits(el){return el.scrollHeight<=el.clientHeight && el.scrollWidth<=el.clientWidth;}
function shrink(el,min){
  let size=parseFloat(getComputedStyle(el).fontSize);
  while(!fits(el) && size>min){size-=1;el.style.fontSize=size+"px";}
}
function fitAll(){
  const copy=document.querySelector(".copy");
  const h=document.querySelector(".headline");
  const b=document.querySelector(".bodycopy");
  shrink(h,36); shrink(b,21);
  let guard=0;
  while(copy.scrollHeight>copy.clientHeight && guard<30){
    let hs=parseFloat(getComputedStyle(h).fontSize);
    let bs=parseFloat(getComputedStyle(b).fontSize);
    if(bs>20)b.style.fontSize=(bs-1)+"px";
    else if(hs>34)h.style.fontSize=(hs-1)+"px";
    else break;
    guard++;
  }
}
fitAll();
"""

def page_html(slide,index):
    headline=clamp_text(slide.get("headline",""),85)
    body=clamp_text(slide.get("body",""),330)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
<div class="slide">
  <div class="header">
    <div class="brand"><span class="brand-dot"></span>LAZY AI ENGINEER</div>
    <div class="counter">{index:02d}/07</div>
  </div>
  <div class="copy">
    <h1 class="{headline_class(headline)}">{e(headline)}</h1>
    <p class="{body_class(body)}">{e(body)}</p>
  </div>
  <div class="visual">{visual_svg(slide)}</div>
  <div class="footer-center">LEARN • BUILD • SHARE</div>
  <div class="footer-left">AI ENGINEERING</div>
  <div class="footer-right">BUILDING IN PUBLIC</div>
</div>
<script>{JS_AUTOFIT}</script>
</body></html>"""

def validate_slides(slides):
    if not isinstance(slides,list):
        raise ValueError("slides must be a list")
    if len(slides)!=7:
        raise ValueError(f"Expected exactly 7 slides, got {len(slides)}")
    allowed={"hero","comparison","flowchart","tools","cards","equation","process"}
    fixed=[]
    for i,s in enumerate(slides,1):
        if not isinstance(s,dict):
            raise ValueError(f"Slide {i} must be an object")
        s=dict(s)
        s["headline"]=clamp_text(s.get("headline",f"Slide {i}"),85)
        s["body"]=clamp_text(s.get("body",""),330)
        vt=str(s.get("visual_type","hero")).lower()
        s["visual_type"]=vt if vt in allowed else "hero"
        if not isinstance(s.get("visual_data"),dict):
            s["visual_data"]={}
        fixed.append(s)
    return fixed

def render_carousel(slides, output_dir=None):
    slides=validate_slides(slides)
    base=Path(__file__).resolve().parent
    out=Path(output_dir) if output_dir else base/"outputs"
    out.mkdir(parents=True,exist_ok=True)

    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":WIDTH,"height":HEIGHT},device_scale_factor=1)
        for i,slide in enumerate(slides,1):
            page.set_content(page_html(slide,i),wait_until="load")
            page.evaluate("fitAll()")
            # Final browser-level overflow safety check.
            overflow=page.evaluate("""() => {
              const c=document.querySelector('.copy');
              return c.scrollHeight>c.clientHeight || c.scrollWidth>c.clientWidth;
            }""")
            if overflow:
                page.evaluate("""() => {
                  document.querySelector('.bodycopy').style.fontSize='20px';
                  document.querySelector('.headline').style.fontSize='34px';
                }""")
            target=out/f"slide_{i}.png"
            page.screenshot(path=str(target),full_page=False)
            print(f"✓ Rendered slide {i}/7 -> {target}")
        browser.close()

if __name__=="__main__":
    print("renderer.py is ready. Run generator.py to create the carousel.")
