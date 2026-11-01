#!/usr/bin/env python3
"""Build an offline spherical viewer from one genuine 2:1 equirectangular image.

Usage: python build_panorama_viewer.py panorama.png viewer.html [--title TITLE]
A 2:1 image is necessary, but cannot prove that imagery is geometrically seamless.
"""
import argparse
import base64
import html
import io
from pathlib import Path

from PIL import Image, ImageOps

TEMPLATE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>html,body{margin:0;height:100%;background:#10151d;color:#fff;font:16px system-ui}canvas{width:100%;height:100%;display:block;touch-action:none;cursor:grab}canvas:active{cursor:grabbing}.panel{position:absolute;left:16px;top:16px;background:#10151ddd;padding:12px;border-radius:8px;max-width:calc(100% - 56px)}h1{font-size:18px;margin:0 0 6px}button{padding:6px 12px;margin-top:8px}#status{font-size:13px}#help{font-size:13px}</style>
<canvas id="view" aria-label="Spherical panorama. Drag or use arrow keys to look around; plus and minus zoom." tabindex="0"></canvas>
<div class="panel"><h1>__TITLE__</h1><div id="help">Drag to look · Pinch / scroll to zoom · Arrow keys · + / −</div><div id="status" role="status">Loading panorama…</div><button id="reset">Reset view</button></div>
<script>
'use strict';
const canvas=document.getElementById('view'),status=document.getElementById('status');
let yaw=0,pitch=0,fov=75,ready=false,queued=false;
const gl=canvas.getContext('webgl',{alpha:false,preserveDrawingBuffer:true});
function fail(message){status.textContent=message;canvas.dataset.ready='error';}
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
function schedule(){if(!queued){queued=true;requestAnimationFrame(render);}}
function render(){queued=false;if(!ready)return;const scale=Math.min(devicePixelRatio||1,2),w=Math.round(innerWidth*scale),h=Math.round(innerHeight*scale);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}gl.viewport(0,0,w,h);gl.uniform2f(size,w,h);gl.uniform3f(view,yaw,pitch,fov*Math.PI/180);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);canvas.dataset.yaw=String(yaw);canvas.dataset.pitch=String(pitch);canvas.dataset.fov=String(fov);status.textContent=`Yaw ${Math.round(yaw*180/Math.PI)}° · Pitch ${Math.round(pitch*180/Math.PI)}° · View ${Math.round(fov)}°`;}
function adjust(dx,dy,zoom=0){yaw=((yaw+dx)%(2*Math.PI)+2*Math.PI)%(2*Math.PI);pitch=Math.max(-Math.PI/2+.001,Math.min(Math.PI/2-.001,pitch+dy));fov=Math.max(30,Math.min(110,fov+zoom));schedule();}
let size,view;
if(!gl){fail('WebGL is unavailable. Open this file in a browser with WebGL enabled.');}else{try{
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec2 position;void main(){gl_Position=vec4(position,0.,1.);}'));
gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`precision highp float;
uniform sampler2D panorama;uniform vec2 size;uniform vec3 view;
void main(){vec2 xy=(gl_FragCoord.xy/size*2.-1.)*tan(view.z/2.);xy.x*=size.x/size.y;
vec3 r=normalize(vec3(xy.x,xy.y,1.));float cp=cos(view.y),sp=sin(view.y);r=vec3(r.x,r.y*cp+r.z*sp,-r.y*sp+r.z*cp);
float cy=cos(view.x),sy=sin(view.x);r=vec3(r.x*cy+r.z*sy,r.y,-r.x*sy+r.z*cy);
vec2 uv=vec2(fract(atan(r.x,r.z)/6.28318530718+.5),.5-asin(clamp(r.y,-1.,1.))/3.14159265359);
gl_FragColor=texture2D(panorama,uv);}`));
gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
const pos=gl.getAttribLocation(program,'position');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);size=gl.getUniformLocation(program,'size');view=gl.getUniformLocation(program,'view');
const img=new Image();img.onerror=()=>fail('Embedded image could not be decoded.');img.onload=()=>{try{if(Math.max(img.width,img.height)>gl.getParameter(gl.MAX_TEXTURE_SIZE))throw Error('Image exceeds this browser’s WebGL texture limit.');const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,img);if(gl.getError()!==gl.NO_ERROR)throw Error('Texture upload failed.');ready=true;canvas.dataset.ready='true';schedule();}catch(e){fail(e.message);}};img.src='data:image/png;base64,__IMAGE__';
}catch(e){fail('Viewer initialization failed: '+e.message);}}
const pointers=new Map();
canvas.addEventListener('pointerdown',e=>{canvas.focus();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});});
canvas.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;const before=[...pointers.values()];const old=pointers.get(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===1){adjust((old.x-e.clientX)*.004,(e.clientY-old.y)*.004);}else if(pointers.size===2){const after=[...pointers.values()];const d=a=>Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);adjust(0,0,(d(before)-d(after))*.15);}});
for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,e=>pointers.delete(e.pointerId));
canvas.addEventListener('wheel',e=>{e.preventDefault();adjust(0,0,Math.sign(e.deltaY)*3);},{passive:false});
canvas.addEventListener('keydown',e=>{const actions={ArrowLeft:[-.08,0],ArrowRight:[.08,0],ArrowUp:[0,.08],ArrowDown:[0,-.08],'+':[0,0,-3],'=':[0,0,-3],'-':[0,0,3]};if(actions[e.key]){e.preventDefault();adjust(...actions[e.key]);}});
document.getElementById('reset').onclick=()=>{yaw=0;pitch=0;fov=75;schedule();};
addEventListener('resize',schedule);
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();ready=false;fail('Graphics context lost. Reload this file to restore the viewer.');});
</script></html>'''


def build_viewer(image_path, output_path, title="Location panorama"):
    image_path, output_path = Path(image_path), Path(output_path)
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite: {output_path}")
    with Image.open(image_path) as source:
        image = ImageOps.exif_transpose(source)
        if image.width != 2 * image.height or image.height < 2:
            raise ValueError("A 2:1 equirectangular image is required (width = 2 × height).")
        encoded = io.BytesIO()
        image.convert("RGB").save(encoded, "PNG")
        dimensions = [image.width, image.height]
    document = TEMPLATE.replace("__TITLE__", html.escape(title, quote=True)).replace(
        "__IMAGE__", base64.b64encode(encoded.getvalue()).decode("ascii")
    )
    # Exclusive creation also protects against a concurrent overwrite.
    with output_path.open("x", encoding="utf-8") as target:
        target.write(document)
    return {"output": str(output_path.resolve()), "dimensions": dimensions,
            "projection": "equirectangular", "offline": True,
            "limitation": "Dimensions do not establish seamlessness or 3D geometry; WebGL required."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("output")
    parser.add_argument("--title", default="Location panorama")
    args = parser.parse_args()
    import json
    print(json.dumps(build_viewer(args.image, args.output, args.title), indent=2))


if __name__ == "__main__":
    main()
