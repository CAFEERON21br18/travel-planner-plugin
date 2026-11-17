from layers import varint
DROP = {"poi", "housenumber", "mountain_peak", "aerodrome_label", "aeroway", "landcover", "park"}
def enc_varint(n):
    o = bytearray()
    while True:
        b = n & 0x7f; n >>= 7
        if n: o.append(b | 0x80)
        else: o.append(b); return bytes(o)
def field(num, wt, payload):
    if wt == 2: return enc_varint(num << 3 | 2) + enc_varint(len(payload)) + payload
    return enc_varint(num << 3) + enc_varint(payload)
def parse(b):
    i = 0; out = []
    while i < len(b):
        key, i = varint(b, i); f, wt = key >> 3, key & 7
        if wt == 0: v, i = varint(b, i)
        elif wt == 2: ln, i = varint(b, i); v = b[i:i+ln]; i += ln
        elif wt == 5: v = b[i:i+4]; i += 4
        elif wt == 1: v = b[i:i+8]; i += 8
        out.append((f, wt, v))
    return out
def raw(f, wt, v):
    if wt == 2: return field(f, 2, v)
    if wt == 0: return field(f, 0, v)
    return enc_varint(f << 3 | wt) + v
def slim_layer(body):
    parts = parse(body)
    keys = [v.decode() for f, wt, v in parts if f == 3]
    vals = [v for f, wt, v in parts if f == 4]
    keep = [k for k in keys if not (k.startswith("name:") or k.startswith("name_"))]
    kmap = {keys.index(k): n for n, k in enumerate(keep)}
    newvals, vmap = [], {}
    feats = []
    for f, wt, v in parts:
        if f != 2: continue
        fp = parse(v); tags = []
        for ff, fwt, fv in fp:
            if ff == 2:
                j = 0; t = []
                while j < len(fv): x, j = varint(fv, j); t.append(x)
                tags = t
        nt = []
        for a, b in zip(tags[0::2], tags[1::2]):
            if a in kmap:
                if b not in vmap: vmap[b] = len(newvals); newvals.append(vals[b])
                nt += [kmap[a], vmap[b]]
        packed = b"".join(enc_varint(x) for x in nt)
        nb = b"".join(raw(ff, fwt, fv) if ff != 2 else field(2, 2, packed) for ff, fwt, fv in fp)
        feats.append(nb)
    out = b""
    for f, wt, v in parts:
        if f == 2: continue
        if f in (3, 4): continue
        out += raw(f, wt, v)
    out += b"".join(field(2, 2, x) for x in feats)
    out += b"".join(field(3, 2, k.encode()) for k in keep)
    out += b"".join(field(4, 2, x) for x in newvals)
    return out
def slim(tile):
    out = b""
    for f, wt, v in parse(tile):
        if f != 3: out += raw(f, wt, v); continue
        name = [x for x in parse(v) if x[0] == 1][0][2].decode()
        if name in DROP: continue
        out += field(3, 2, slim_layer(v))
    return out
