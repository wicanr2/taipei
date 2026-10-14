"""#60: readiness only; exact ROM sources or the observed native cursor variant."""
from hd_source_audit import cell, MATERIAL


def locate_small_cursor(frame, aliases):
    """Locate the observed one-cell border over an exact original ROM interior."""
    variants=set()
    for source in aliases:
        raw=bytearray(source)
        for dx in range(9):raw[dx]=15 if dx%2==0 else 0
        for dy in range(9):raw[dy*9]=15; raw[dy*9+8]=15
        for dx in range(9):raw[72+dx]=15 if dx%2==0 else 0
        variants.add(bytes(raw))
    found=[(x,y) for y in range(15) for x in range(29)
        if cell(frame,5+x*9,34+y*9) not in aliases and cell(frame,5+x*9,34+y*9) in variants]
    assert len(found)==1,('原版單格游標不唯一',found)
    return list(found[0])


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
