#!/usr/bin/env python3
from pwn import *

pwds = [
    "C3u3CFwCxQGwgwSw",
    "vMARD2XnAgfwzKOc",
    "zkz0zEgAkGTjfZg9",
    "xkIaLIHjn3ILsWdC",
    "hePjRo3GWAxiCyp2",
    "pUsXfn0wOgE1fkT2",
    "Kv3K7Gxh2Fsqkxzu",
    "OTNWXWexnLb9GiBj",
    "yNHva8BxFqPST63c",
    "gKBQxTt0WvT3TWN3",
    "bNHGHh4XbCrq8B3Z",
    "ymlOuFyRaCNAAtvE"
]

keys = []
for t in range(12):
    with open(f'keys/{t}.key', 'r') as f:
        keys.append(f.read().strip())

def copy_key(team_id):
    s = ssh(host=f"10.60.{team_id}.1", user='root', password=pwds[team_id])
    sh = s.process(['/bin/sh'])

    sh.sendline(b'cd /root')
    sh.sendline(f"echo '{keys[team_id]}' > m0leCoin.key".encode())
    s.close()

def main():
    for i in range(12):
        print(f'Pushing team key #{i}')
        copy_key(i)
    print('DONE')

if __name__ == '__main__':
    main()
