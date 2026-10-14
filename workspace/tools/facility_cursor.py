"""#60: readiness only; exact ROM sources or the observed native cursor variant."""
from hd_source_audit import cell, MATERIAL


class ConstructionGate:
    def __init__(self, aliases):
        self.sources={raw for raw in aliases if not set(raw)<=MATERIAL}
        self.cache={}

    def variants(self,x,y,w,h):
        key=(x==0,x==w-1,y==0,y==h-1,x%2)
        if key in self.cache:return self.cache[key]
        variants=set()
        for source in self.sources:
            raw=bytearray(source)
            if y==0:
                for dx in range(9):raw[dx]=15 if (x*9+dx)%2==0 else 0
            if x==0:
                for dy in range(9):raw[dy*9]=15
            if x==w-1:
                for dy in range(9):raw[dy*9+8]=15
            if y==h-1:
                for dx in range(9):raw[72+dx]=15 if (x*9+dx)%2==0 else 0
            variants.add(bytes(raw))
        self.cache[key]=variants
        return variants

    def ready(self,frame,col,row,w,h):
        for y in range(h):
            for x in range(w):
                raw=cell(frame,5+(col+x)*9,34+(row+y)*9)
                if raw not in self.sources and raw not in self.variants(x,y,w,h):return False
        return True
