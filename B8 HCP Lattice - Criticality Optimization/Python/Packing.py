import numpy as np
import pandas as pd


def calc_hcp_coords(r, n):
    try:
        df = pd.read_csv('./Python/hcp_coords.csv') 
    except: 
        df = pd.read_csv('./hcp_coords.csv') # ./Python/
    df['cnorm'] = df.apply(lambda row : np.linalg.norm([row['r'], row['z']], ord=np.inf), axis = 1)
    df = df.sort_values(by='cnorm', axis=0, ignore_index=True)

    h = r # half height
    head = df.head(n)
    max_h = max(np.abs(head['z'].max()), np.abs(head['z'].min()))
    max_r = np.abs(head['r'].max())
    scale = min(r/max_r, h/max_h)

    p = 6
    head.loc[:,['x','y','z']] *= scale
    head.map(lambda x: np.trunc(x*10**p)/(10**p))
    out = head[['x','y','z']].to_numpy()
    out = np.around(out, p)

    # round all to 6 sigfigs for mcnp 80 char per line limit
    # p = 6
    # outp = np.where(np.isfinite(out) & (out != 0), np.abs(out), 10**(p-1))
    # mags = 10 ** (p - 1 - np.floor(np.log10(outp)))
    # out = np.round(out * mags) / mags
    
    # print(f"  comment. Packing.py last element of out array: {out[-1]}")
    # np.savetxt('testing.txt', out[-1], delimiter=',',fmt='%1.6e')
    return out

# # np.savetxt('test.txt', gen_ksrc_coords(61.1154577633,1400), delimiter=',',fmt='%1.6e')

# def get_r(vec):
#     _df = pd.DataFrame(vec, columns=['x', 'y', 'z'])
#     _df['r'] = _df.apply(lambda row : np.linalg.norm([row['x'], row['y']]), axis = 1)
#     return _df['r'].max()

# def get_h(vec):
#     _df = pd.DataFrame(vec, columns=['x', 'y', 'z'])
#     return _df['z'].max()-_df['z'].min()

# def main():
#     r = 65.6154577633
#     h = r*2
#     v = gen_ksrc_coords(r-4.5, 1400)

#     print(f'height = {get_h(v)}')
#     print(f'radius = {get_r(v)}')
#     print(f'height max = {h}')
#     print(f'radius max = {r}')

# main()