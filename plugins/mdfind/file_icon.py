file_icons = {"*": "file", "folder": "folder", "lnk": "shortcut","xsh":"console",
              "html": "html", "htm": "html", "xhtml": "html", "html_vm": "html", "asp": "html",
              "jade": "pug",
              "pug": "pug",
              "md": "markdown", "markdown": "markdown", "rst": "markdown",
              "blink": "blink",
              "css": "css",
              "scss": "sass", "sass": "sass",
              "less": "less",
              "json": "json", "tsbuildinfo": "json", "json5": "json",
              "jinja": "jinja", "jinja2": "jinja", "j2": "jinja",
              "sublime-project": "sublime", "sublime-workspace": "sublime",
              "yaml": "yaml", "YAML-tmLanguage": "yaml", "yml": "yaml",
              "xml": "xml", "plist": "xml", "xsd": "xml", "dtd": "xml", "xsl": "xml", "xslt": "xml", "resx": "xml",
              "iml": "xml",
              "xquery": "xml", "tmLanguage": "xml", "manifest": "xml", "project": "xml", "png": "image",
              "jpeg": "image",
              "jpg": "image", "gif": "image", "ico": "image", "tif": "image", "tiff": "image", "psd": "image",
              "psb": "image", "ami": "image", "apx": "image", "bmp": "image", "bpg": "image", "brk": "image",
              "cur": "image", "dds": "image", "dng": "image", "exr": "image", "fpx": "image", "gbr": "image",
              "img": "image", "jbig2": "image", "jb2": "image", "jng": "image", "jxr": "image", "pbm": "image",
              "pgf": "image", "pic": "image", "raw": "image", "webp": "image", "eps": "image", "afphoto": "image",
              "ase": "image", "aseprite": "image", "clip": "image", "cpt": "image", "heif": "image", "heic": "image",
              "kra": "image", "mdp": "image", "ora": "image", "pdn": "image", "reb": "image", "sai": "image",
              "tga": "image", "xcf": "image", "js": "javascript", "esx": "javascript", "mjs": "javascript",
              "jsx": "react", "tsx": "react_ts", "routing.ts": "routing", "routing.tsx": "routing",
              "routing.js": "routing", "routing.jsx": "routing", "routes.ts": "routing", "routes.tsx": "routing",
              "routes.js": "routing", "routes.jsx": "routing", "action.js": "redux-action",
              "actions.js": "redux-action",
              "action.ts": "redux-action", "actions.ts": "ngrx-actions", "reducer.js": "redux-reducer",
              "reducers.js": "redux-reducer", "reducer.ts": "ngrx-reducer", "reducers.ts": "redux-reducer",
              "store.js": "vuex-store", "store.ts": "vuex-store", "ini": "settings", "dlc": "settings",
              "dll": "settings", "config": "settings", "conf": "settings", "properties": "settings", "prop": "settings",
              "settings": "settings", "option": "settings", "props": "settings", "toml": "settings",
              "prefs": "settings",
              "sln.dotsettings": "settings", "sln.dotsettings.user": "settings", "cfg": "settings", "ts": "typescript",
              "d.ts": "typescript-def", "marko": "markojs", "pdf": "pdf", "xlsx": "table", "xls": "table",
              "csv": "table", "tsv": "table", "vscodeignore": "vscode", "vsixmanifest": "vscode", "vsix": "vscode",
              "code-workplace": "vscode", "csproj": "visualstudio", "ruleset": "visualstudio", "sln": "visualstudio",
              "suo": "visualstudio", "vb": "visualstudio", "vbs": "visualstudio", "vcxitems": "visualstudio",
              "vcxitems.filters": "visualstudio", "vcxproj": "visualstudio", "vcxproj.filters": "visualstudio",
              "pdb": "database", "sql": "database", "pks": "database", "pkb": "database", "accdb": "database",
              "mdb": "database", "sqlite": "database", "pgsql": "database", "postgres": "database", "psql": "database",
              "cs": "csharp", "csx": "csharp", "qs": "qsharp", "zip": "zip", "tar": "zip", "gz": "zip", "xz": "zip",
              "br": "zip", "bzip2": "zip", "gzip": "zip", "brotli": "zip", "7z": "zip", "rar": "zip", "tgz": "zip",
              "zig": "zig", "exe": "exe", "msi": "exe", "java": "java", "jar": "java", "jsp": "java", "c": "c",
              "m": "c",
              "i": "c", "mi": "c", "h": "h", "cc": "cpp", "cpp": "cpp", "cxx": "cpp", "c++": "cpp", "cp": "cpp",
              "mm": "cpp", "mii": "cpp", "ii": "cpp", "hh": "hpp", "hpp": "hpp", "hxx": "hpp", "h++": "hpp",
              "hp": "hpp",
              "tcc": "hpp", "inl": "hpp", "go": "go", "py": "python", "pyc": "python-misc", "whl": "python-misc",
              "url": "url", "sh": "console", "ksh": "console", "csh": "console", "tcsh": "console", "zsh": "console",
              "bash": "console", "bat": "console", "cmd": "console", "awk": "console", "fish": "console",
              "ps1": "powershell", "psm1": "powershell", "psd1": "powershell", "ps1xml": "powershell",
              "psc1": "powershell", "pssc": "powershell", "gradle": "gradle", "doc": "word", "docx": "word",
              "rtf": "word", "cer": "certificate", "cert": "certificate", "crt": "certificate", "pub": "key",
              "key": "key", "pem": "key", "asc": "key", "gpg": "key", "woff": "font", "woff2": "font", "ttf": "font",
              "eot": "font", "suit": "font", "otf": "font", "bmap": "font", "fnt": "font", "odttf": "font",
              "ttc": "font", "font": "font", "fonts": "font", "sui": "font", "ntf": "font", "mrf": "font", "lib": "lib",
              "bib": "lib", "rb": "ruby", "erb": "ruby", "fs": "fsharp", "fsx": "fsharp", "fsi": "fsharp",
              "fsproj": "fsharp", "swift": "swift", "ino": "arduino", "dockerignore": "docker", "dockerfile": "docker",
              "tex": "tex", "cls": "tex", "sty": "tex", "dtx": "tex", "ltx": "tex", "pptx": "powerpoint",
              "ppt": "powerpoint", "pptm": "powerpoint", "potx": "powerpoint", "potm": "powerpoint",
              "ppsx": "powerpoint", "ppsm": "powerpoint", "pps": "powerpoint", "ppam": "powerpoint",
              "ppa": "powerpoint",
              "webm": "video", "mkv": "video", "flv": "video", "vob": "video", "ogv": "video", "ogg": "video",
              "gifv": "video", "avi": "video", "mov": "video", "qt": "video", "wmv": "video", "yuv": "video",
              "rm": "video", "rmvb": "video", "mp4": "video", "m4v": "video", "mpg": "video", "mp2": "video",
              "mpeg": "video", "mpe": "video", "mpv": "video", "m2v": "video", "vdi": "virtual", "vbox": "virtual",
              "vbox-prev": "virtual", "ics": "email", "mp3": "audio", "flac": "audio", "m4a": "audio", "wma": "audio",
              "aiff": "audio", "coffee": "coffee", "cson": "coffee", "iced": "coffee", "txt": "document",
              "graphql": "graphql", "gql": "graphql", "rs": "rust", "raml": "raml", "xaml": "xaml", "hs": "haskell",
              "kt": "kotlin", "kts": "kotlin", "patch": "git", "lua": "lua", "clj": "clojure", "cljs": "clojure",
              "cljc": "clojure", "groovy": "groovy", "r": "r", "rmd": "r", "dart": "dart", "as": "actionscript",
              "mxml": "mxml", "ahk": "autohotkey", "swf": "flash", "swc": "swc", "cmake": "cmake", "asm": "assembly",
              "a51": "assembly", "inc": "assembly", "nasm": "assembly", "s": "assembly", "ms": "assembly",
              "agc": "assembly", "ags": "assembly", "aea": "assembly", "argus": "assembly", "mitigus": "assembly",
              "binsource": "assembly", "vue": "vue", "ml": "ocaml", "mli": "ocaml", "cmx": "ocaml",
              "js.map": "javascript-map", "mjs.map": "javascript-map", "css.map": "css-map", "lock": "lock",
              "hbs": "handlebars", "mustache": "handlebars", "pm": "perl", "hx": "haxe", "spec.ts": "test-ts",
              "e2e-spec.ts": "test-ts", "test.ts": "test-ts", "ts.snap": "test-ts", "spec.tsx": "test-jsx",
              "test.tsx": "test-jsx", "tsx.snap": "test-jsx", "spec.jsx": "test-jsx", "test.jsx": "test-jsx",
              "jsx.snap": "test-jsx", "spec.js": "test-js", "e2e-spec.js": "test-js", "test.js": "test-js",
              "js.snap": "test-js", "module.ts": "nest-module", "module.js": "nest-module", "ng-template": "angular",
              "component.ts": "angular-component", "component.js": "angular-component", "guard.ts": "nest-guard",
              "guard.js": "nest-guard", "service.ts": "nest-service", "service.js": "nest-service",
              "pipe.ts": "nest-pipe", "pipe.js": "nest-pipe", "filter.js": "nest-filter",
              "directive.ts": "angular-directive", "directive.js": "angular-directive",
              "resolver.ts": "angular-resolver", "resolver.js": "angular-resolver", "pp": "puppet", "ex": "elixir",
              "exs": "elixir", "eex": "elixir", "leex": "elixir", "ls": "livescript", "erl": "erlang", "twig": "twig",
              "jl": "julia", "elm": "elm", "pure": "purescript", "purs": "purescript", "tpl": "smarty",
              "styl": "stylus",
              "re": "reason", "rei": "reason", "cmj": "bucklescript", "merlin": "merlin", "v": "verilog",
              "vhd": "verilog", "sv": "verilog", "svh": "verilog", "nb": "mathematica", "wl": "wolframlanguage",
              "wls": "wolframlanguage", "njk": "nunjucks", "nunjucks": "nunjucks", "robot": "robot", "sol": "solidity",
              "au3": "autoit", "haml": "haml", "yang": "yang", "mjml": "mjml", "tf": "terraform",
              "tf.json": "terraform",
              "tfvars": "terraform", "tfstate": "terraform", "blade.php": "laravel", "inky.php": "laravel",
              "applescript": "applescript", "cake": "cake", "feature": "cucumber", "nim": "nim", "nimble": "nim",
              "apib": "apiblueprint", "apiblueprint": "apiblueprint", "riot": "riot", "tag": "riot", "vfl": "vfl",
              "kl": "kl", "pcss": "postcss", "sss": "postcss", "todo": "todo", "cfml": "coldfusion",
              "cfc": "coldfusion",
              "lucee": "coldfusion", "cfm": "coldfusion", "cabal": "cabal", "nix": "nix", "slim": "slim",
              "http": "http",
              "rest": "http", "rql": "restql", "restql": "restql", "kv": "kivy", "graphcool": "graphcool", "sbt": "sbt",
              "apk": "android", "env": "tune", "gitlab-ci.yml": "gitlab", "jenkinsfile": "jenkins",
              "jenkins": "jenkins",
              "rootReducer.ts": "ngrx-reducer", "state.ts": "ngrx-state", "effects.ts": "ngrx-effects", "cr": "crystal",
              "ecr": "crystal", "drone.yml": "drone", "cu": "cuda", "cuh": "cuda", "log": "log", "def": "dotjs",
              "dot": "dotjs", "jst": "dotjs", "ejs": "ejs", ".wakatime-project": "wakatime", "pde": "processing",
              "stories.js": "storybook", "stories.jsx": "storybook", "story.js": "storybook", "story.jsx": "storybook",
              "stories.ts": "storybook", "stories.tsx": "storybook", "story.ts": "storybook", "story.tsx": "storybook",
              "wpy": "wepy", "hcl": "hcl", "san": "san", "djt": "django", "red": "red", "fxp": "foxpro",
              "prg": "foxpro",
              "pot": "i18n", "po": "i18n", "mo": "i18n", "wat": "webassembly", "wasm": "webassembly",
              "ipynb": "jupyter",
              "d": "d", "mdx": "mdx", "bal": "ballerina", "balx": "ballerina", "rkt": "racket", "bzl": "bazel",
              "bazel": "bazel", "mint": "mint", "vm": "velocity", "fhtml": "velocity", "vtl": "velocity", "gd": "godot",
              "godot": "godot-assets", "tres": "godot-assets", "tscn": "godot-assets",
              "azure-pipelines.yml": "azure-pipelines", "azure-pipelines.yaml": "azure-pipelines", "azcli": "azure",
              "vagrantfile": "vagrant", "prisma": "prisma", "cshtml": "razor", "vbhtml": "razor", "ad": "asciidoc",
              "adoc": "asciidoc", "asciidoc": "asciidoc", "edge": "edge", "ss": "scheme", "scm": "scheme", "stl": "3d",
              "obj": "3d", "ac": "3d", "blend": "3d", "mesh": "3d", "mqo": "3d", "pmd": "3d", "pmx": "3d", "skp": "3d",
              "vac": "3d", "vdp": "3d", "vox": "3d", "svg": "svg", "svelte": "svelte", "vimrc": "vim", "gvimrc": "vim",
              "exrc": "vim", "controller.ts": "nest-controller", "controller.js": "nest-controller",
              "middleware.ts": "nest-middleware", "middleware.js": "nest-middleware", "decorator.ts": "nest-decorator",
              "decorator.js": "nest-decorator", "filter.ts": "nest-filter", "gateway.ts": "nest-gateway",
              "gateway.js": "nest-gateway", "moon": "moonscript", "prw": "advpl_prw", "prx": "advpl_prw",
              "ptm": "advpl_ptm", "tlpp": "advpl_tlpp", "ch": "advpl_include", "iso": "disc", "f": "fortran",
              "f77": "fortran", "f90": "fortran", "f95": "fortran", "f03": "fortran", "f08": "fortran",
              "liquid": "liquid", "p": "prolog", "pro": "prolog", "coco": "coconut", "sketch": "sketch"}
