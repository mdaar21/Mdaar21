def actor(light=False,bar=False):
 barbell='''<g class="barbell" transform="translate(0 0)" stroke="#f9f5e9" stroke-width="16" paint-order="stroke fill" stroke-linejoin="round"><rect x="48" y="228" width="424" height="14" rx="7" fill="#121210"/><rect x="28" y="182" width="52" height="106" rx="10" fill="#d1ac65"/><rect x="80" y="196" width="25" height="78" rx="5" fill="#121210"/><rect x="440" y="182" width="52" height="106" rx="10" fill="#d1ac65"/><rect x="415" y="196" width="25" height="78" rx="5" fill="#121210"/></g>''' if bar else ''
 return '''<div class="character '''+('light-kit' if light else '')+'''"><svg class="actor" viewBox="0 0 520 700" role="img" aria-label="شخصية مدار الكرتونية بوجه خالٍ تمامًا من الملامح"><g class="person" stroke="#f9f5e9" stroke-width="18" stroke-linecap="round" stroke-linejoin="round" paint-order="stroke fill">'''+barbell+'''
 <g class="leg-l" transform="rotate(0 228 427)"><path d="M204 409H258L241 606H190L202 460Z" fill="#121210"/><ellipse cx="215" cy="625" rx="49" ry="25" fill="#f3ebd8"/></g>
 <g class="leg-r" transform="rotate(0 292 427)"><path d="M262 409H316L329 606H278L264 460Z" fill="#121210"/><ellipse cx="305" cy="625" rx="49" ry="25" fill="#f3ebd8"/></g>
 <rect x="238" y="194" width="44" height="58" rx="9" fill="#d9a171"/>
 <g class="arm-l" transform="rotate(0 185 245)"><path d="M184 244Q174 240 168 253L129 338Q123 355 143 362Q161 365 166 348L204 260Q210 246 194 242Z" fill="#d9a171"/>
  <g class="fore-l" transform="rotate(0 145 345)"><path d="M128 344Q126 330 143 329Q159 328 161 344L167 433Q170 455 151 460Q130 461 128 441Z" fill="#d9a171"/><circle cx="150" cy="440" r="23" fill="#d9a171"/><circle cx="145" cy="345" r="18" stroke="none" fill="#d9a171"/><path class="pointer-l" d="M138 451L136 479Q136 491 148 491Q161 491 161 478L161 450Z" fill="#d9a171"/></g>
 </g>
 <g class="arm-r" transform="rotate(0 335 245)"><path d="M336 244Q346 240 352 253L391 338Q397 355 377 362Q359 365 354 348L316 260Q310 246 326 242Z" fill="#d9a171"/>
  <g class="fore-r" transform="rotate(0 375 345)"><path d="M392 344Q394 330 377 329Q361 328 359 344L353 433Q350 455 369 460Q390 461 392 441Z" fill="#d9a171"/><circle cx="370" cy="440" r="23" fill="#d9a171"/><circle cx="375" cy="345" r="18" stroke="none" fill="#d9a171"/><path class="pointer-r" d="M359 451L359 479Q359 491 371 491Q384 491 383 478L382 450Z" fill="#d9a171"/></g>
 </g>
 <path class="jersey" d="M186 225Q260 209 334 225L348 407Q260 426 172 407Z" fill="#d1ac65"/>
 <path d="M177 365H343L344 388H176Z" stroke="none" fill="#121210"/>
 <rect x="178" y="411" width="164" height="51" rx="25" fill="#121210"/>
 <g class="head" transform="rotate(0 260 145)"><path class="face" d="M195 145C190 104 216 72 260 72C306 72 328 100 325 145C326 183 296 216 260 216C224 216 194 185 195 145Z" fill="#d9a171"/><path class="hair" d="M195 145C190 104 216 72 260 72C306 72 328 100 325 145H215V160H195Z" fill="#121210" stroke="none"/></g>
 </g></svg></div>'''
