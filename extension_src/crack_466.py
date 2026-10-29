"""Dot Bypasser 4.6.6 (Chrome MV3) - full-access patch.

Mirrors the proven 4.6.5 crack recipe onto 4.6.6:

  P1  anti-debug      : strip every `debugger;` statement in the shipped bundles
  P2  premium RPC     : background `isPremium` handler returns a premium payload
  P3  premium compare : `premium < 1.1 || false`  ->  `true`  (UI + settings + content script)
  P4  storage seed    : pre-set `enabled` / `hasAgreedDisclaimer` on every SW start
  P5  unofficial gate : integrity ("Unofficial Source") modal can never open

Usage: python crack_466.py <extension-folder>
"""
import os
import re
import sys

root = sys.argv[1]
log = []


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def write(p, s):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)


def sub_once(path, old, new, label):
    s = read(path)
    n = s.count(old)
    if n != 1:
        log.append(f'  !! {label}: expected 1 match, found {n} - SKIPPED')
        return False
    write(path, s.replace(old, new))
    log.append(f'  ok {label}')
    return True


# ---------------------------------------------------------------- P0 self-check guards
# The bundles wrap hot functions in anti-tamper guards:
#   if(NAME===<magic>){return FN(...arguments)}else{while(true){}}
# Editing the guarded function changes its source hash, the magic no longer matches
# and the page locks in an infinite loop. Rewrite every guard to call through.
guard_pat = re.compile(
    r'if\([A-Za-z_$][\w$]*===\d{12,17}\)\{return ([A-Za-z_$][\w$]*)\(\.\.\.arguments\)\}else\{while\(true\)\{\}\}'
)
for rel in ('chunks/main-D9uk0BkO.js', 'chunks/Settings-3vmFYYj7.js',
            'chunks/Unofficial-DSGqBefk.js', 'chunks/GatewayesSetting-DsAs5-Ri.js',
            'chunks/GatewaysSetting-DsAs5-Ri.js', 'chunks/Modal-DVtKSfYm.js',
            'chunks/BinHistory-Z8ewo9xL.js', 'chunks/CustomGatewaysSetting-DVHwT5VN.js',
            'chunks/Fingerprint-CnKJ_vSA.js', 'chunks/fingerprint-DeHcGO4s.js',
            'chunks/offscreen-BJAn1Uau.js', 'content-scripts/main.js',
            'content-scripts/content.js', 'background.js'):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        continue
    s = read(p)
    n = len(guard_pat.findall(s))
    if not n:
        continue
    write(p, guard_pat.sub(lambda m: 'return ' + m.group(1) + '(...arguments)', s))
    log.append(f'P0 {rel}: neutralised {n} self-check guards')

# ---------------------------------------------------------------- P1 anti-debug
for rel in ('background.js', 'chunks/main-D9uk0BkO.js',
            'chunks/Settings-3vmFYYj7.js', 'chunks/Unofficial-DSGqBefk.js'):
    p = os.path.join(root, rel)
    s = read(p)
    n = s.count('debugger;')
    if not n:
        continue
    if n != s.count('debugger;'):
        pass
    write(p, s.replace('debugger;', ';'))
    log.append(f'P1 {rel}: removed {n} `debugger;` statements')

# ---------------------------------------------------------------- P2 premium RPC
bg = os.path.join(root, 'background.js')
stub = 'function fibHauF(){"use strict";var[[],yMTXohL]=arguments}'
sub_once(bg, stub,
         'function fibHauF(){"use strict";var[[],yMTXohL]=arguments;return{premium:0}}',
         'P2 background isPremium handler -> {premium:0}')

# ---------------------------------------------------------------- P3 premium flag
pat = re.compile(r'[A-Za-z_$][\w$]*<1\.1\|\|![A-Za-z_$][\w$]*(?:\[0x[0-9a-fA-F]+\])?')
for rel in ('chunks/main-D9uk0BkO.js', 'chunks/Settings-3vmFYYj7.js',
            'content-scripts/main.js', 'content-scripts/content.js'):
    p = os.path.join(root, rel)
    s = read(p)
    hits = pat.findall(s)
    if not hits:
        log.append(f'P3 {rel}: no premium comparison found')
        continue
    write(p, pat.sub('!0', s))
    log.append(f'P3 {rel}: premium forced true ({len(hits)} site(s))')

# ---------------------------------------------------------------- P5 unofficial gate
mp = os.path.join(root, 'chunks/main-D9uk0BkO.js')
sub_once(mp, '(fc()||!(await Bp()))', '!1',
         'P5 integrity gate -> never opens "Unofficial Source"')

# ---------------------------------------------------------------- P4 storage seed
seed = 'chrome.storage.local.set({"enabled":true,"hasAgreedDisclaimer":true});'
s = read(bg)
if not s.startswith(seed):
    write(bg, seed + s)
    log.append('P4 background.js: storage seeded (enabled, hasAgreedDisclaimer)')
else:
    log.append('P4 background.js: seed already present')

print('\n'.join(log))
