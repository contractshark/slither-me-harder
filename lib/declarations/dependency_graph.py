from slither.solc_parsing.declarations.contract import ContractSolc04
from slither.solc_parsing.declarations.function import FunctionSolc

class DependencyFunction:
    def __init__(self, slither_function):
        self._slither_function = slither_function
        self._name = slither_function.name
        self._read = set()
        self._write = set()

    @property
    def slither_function(self):
        return self._slither_function

    @property
    def name(self):
        return self._name

    @property
    def read(self):
        return self._read

    @property
    def write(self):
        return self._write

    def add_read(self, obj):
        self._read.add(obj)

    def add_write(self, obj):
        self._write.add(obj)


class DependencyStateVariable:
    def __init__(self, slither_state_variable):
        self._slither_state_variable = slither_state_variable
        self._name = slither_state_variable.name
        self._read_by = set()
        self._written_by = set()

    @property
    def slither_state_variable(self):
        return self._slither_state_variable

    @property
    def name(self):
        return self._name

    @property
    def read_by(self):
        return self._read_by

    @property
    def written_by(self):
        return self._written_by

    def add_read_by(self, obj):
        self._read_by.add(obj)

    def add_written_by(self, obj):
        self._written_by.add(obj)


class DependencyGraph:
    def __init__(self, slither_contract: ContractSolc04):
        self._functions = dict()  # canonical_name as key
        self._state_variables = dict()  # name as key

        self._construct_dependency_graph(slither_contract)
        self._dot_graph = DotGraph(self.functions.values())
        html = self._dot_graph.html
        f = open(f'./dependency_graphs/{slither_contract.name}.html', 'w')
        f.write(html)
        f.close()

    @property
    def functions(self):
        return self._functions

    @property
    def state_variables(self):
        return self._state_variables

    def _construct_dependency_graph(self, slither_contract: ContractSolc04):
        for slither_f in slither_contract.functions:
            new_function = DependencyFunction(slither_f)
            self._functions[slither_f.canonical_name] = new_function
            nodes = set()
            for ir in slither_f.all_slithir_operations():
                nodes.add(ir.node)

            for node in nodes:
                for v in node.state_variables_read:
                    if not self.state_variables.get(v.name):
                        sv = DependencyStateVariable(v)
                        self._state_variables[v.name] = sv
                        new_function.add_read(sv)
                        sv.add_read_by(new_function)
                    else:
                        sv = self.state_variables.get(v.name)
                        new_function.add_read(sv)
                        sv.add_read_by(new_function)

                for v in node.state_variables_written:
                    if not self.state_variables.get(v.name):
                        sv = DependencyStateVariable(v)
                        self._state_variables[v.name] = sv
                        new_function.add_write(sv)
                        sv.add_written_by(new_function)
                    else:
                        sv = self.state_variables.get(v.name)
                        new_function.add_write(sv)
                        sv.add_written_by(new_function)


from pydot import Dot, Node, Edge


class DotGraph:
    def __init__(self, functions):
        self.node_dic = {}
        self.edge_dic = {}
        self.graph = Dot()
        self.html = None

        for f in functions:
            if f.name in ['slitherConstructorVariables', 'slitherConstructorConstantVariables']:
                continue
            self.construct_node(f)

        self.construct_graph(functions)
        self.html = svg_to_html(self.graph.create_svg().decode('utf-8'))

    def construct_node(self, function):
        n = Node(function.name)
        n.set_tooltip(construct_tooltip(function))
        self.node_dic[function.name] = n
        self.graph.add_node(n)

    def construct_graph(self, functions):
        for f in functions:
            if (f.name in ['slitherConstructorVariables', 'slitherConstructorConstantVariables'] or
                    f.slither_function.is_constructor):
                continue

            for sr in f.read:
                for written_f in sr.written_by:
                    if written_f.name not in ['slitherConstructorVariables', 'slitherConstructorConstantVariables']:
                        n1 = self.get_node(f.name)
                        n2 = self.get_node(written_f.name)
                        if self.edge_dic.get((n1, n2)):
                            e = self.edge_dic[(n1, n2)]
                            old_label = e.get_label()
                            e.set_label(f'{old_label.strip()}, {sr.name}        ')
                        else:
                            self.construct_edge(n1, n2)
                            e = self.edge_dic[(n1, n2)]
                            e.set_label(f'{sr.name}        ')

    def construct_edge(self, _n1: Node, _n2: Node):
        e = Edge(_n1, _n2, fontsize="8", fontcolor="#2E86C1", arrowsize="0.7")
        self.edge_dic[(_n1, _n2)] = e
        self.graph.add_edge(e)

    def get_node(self, _name):
        return self.node_dic.get(_name)


def construct_tooltip(function):
    """
    Takes a Function object and constructs the tooltip for it to be displayed in the DOT graph.

    Finished.
    """
    res = list()

    res.append('Function: ')
    res.append(f'\t{function.slither_function.canonical_name}')

    res.append('---')
    res.append('Modifiers: ')
    for m in function.slither_function.modifiers:
        res.append(f'\t{m.name}')

    res.append('---')
    res.append('State Variables Read: ')
    for sv in function.read:
        res.append(f'\t{sv.name}')

    res.append('---')
    res.append('State Variables Written: ')
    for sv in function.write:
        res.append(f'\t{sv.name}')

    return '\n'.join(res)


def svg_to_html(_svg: str):
    """
    https://github.com/usyd-blockchain/vandal/blob/07ee51e86ddf6527c6bc39e6cd902b6cc9d6c346/src/exporter.py

    This function is mostly copied from Vandal.

    Finished.
    """
    lines = _svg.split("\n")
    page = list()

    page.append("""
              <html>
              <body>
              <style>
              .node
              {
                transition: all 0.05s ease-out;
              }
              .node:hover
              {
                stroke-width: 1.5;
                cursor:pointer
              }
              .node:hover
              ellipse
              {
                fill: #EEE;
              }
              textarea#infobox {
                position: fixed;
                display: block;
                top: 0;
                right: 0;
              }
              .dropbutton {
                padding: 10px;
                border: none;
              }
              .dropbutton:hover, .dropbutton:focus {
                background-color: #777777;
              }
              .dropdown {
                margin-right: 5px;
                position: fixed;
                top: 5px;
                right: 0px;
              }
              .dropdown-content {
                background-color: white;
                display: none;
                position: absolute;
                width: 70px;
                box-shadow: 0px 5px 10px 0px rgba(0,0,0,0.2);
                z-index: 1;
              }
              .dropdown-content a {
                color: black;
                padding: 8px 10px;
                text-decoration: none;
                font-size: 10px;
                display: block;
              }
              .dropdown-content a:hover { background-color: #f1f1f1; }
              .show { display:block; }
              </style>
              """)

    for line in lines[3:]:
        page.append(line)

    page.append("""<textarea id="infobox" disabled=true rows=40 cols=80></textarea>""")

    page.append("""<script>""")

    page.append("""
               // Set info textbox contents to the title of the given element, with line endings replaced suitably.
               function setInfoContents(element){
                   document.getElementById('infobox').value = element.getAttribute('xlink:title').replace(/\\\\n/g, '\\n');
               }
               // Make all node anchor tags in the svg clickable.
               for (var el of Array.from(document.querySelectorAll(".node a"))) {
                   el.setAttribute("onclick", "setInfoContents(this);");
               }
               const svg = document.querySelector('svg')
               const NS = "http://www.w3.org/2000/svg";
               const defs = document.createElementNS( NS, "defs" );
               // IIFE add filter to svg to allow shadows to be added to nodes within it
               (function(){
                 defs.innerHTML = makeShadowFilter()
                 svg.insertBefore(defs,svg.children[0])
               })()
               function colorToID(color){
                 return color.replace(/[^a-zA-Z0-9]/g,'_')
               }
               function makeShadowFilter({color = 'black',x = 0,y = 0, blur = 3} = {}){
                 return `
                 <filter id="filter_${colorToID(color)}" x="-40%" y="-40%" width="250%" height="250%">
                   <feGaussianBlur in="SourceAlpha" stdDeviation="${blur}"/>
                   <feOffset dx="${x}" dy="${y}" result="offsetblur"/>
                   <feFlood flood-color="${color}"/>
                   <feComposite in2="offsetblur" operator="in"/>
                   <feMerge>
                     <feMergeNode/>
                     <feMergeNode in="SourceGraphic"/>
                   </feMerge>
                 </filter>
                 `
               }
               // Shadow toggle functions, with filter caching
               function addShadow(el, {color = 'black', x = 0, y = 0, blur = 3}){
                 const id = colorToID(color);
                 if(!defs.querySelector(`#filter_${id}`)){
                   const d = document.createElementNS(NS, 'div');
                   d.innerHTML = makeShadowFilter({color, x, y, blur});
                   defs.appendChild(d.children[0]);
                 }
                 el.style.filter = `url(#filter_${id})`
               }
               function removeShadow(el){
                 el.style.filter = ''
               }
               function hash(n) {
                 var str = n + "rainbows" + n + "please" + n;
                 var hash = 0;
                 for (var i = 0; i < str.length; i++) {
                   hash = (((hash << 5) - hash) + str.charCodeAt(i)) | 0;
                 }
                 return hash > 0 ? hash : -hash;
               };
               function getColor(n, sat="80%", light="50%") {
                 const hue = hash(n) % 360;
                 return `hsl(${hue}, ${sat}, ${light})`;
               }
               // Add shadows to function body nodes, and highlight functions in the dropdown list
               function highlightFunction(i) {
                 for (var n of Array.from(document.querySelectorAll(".node ellipse"))) {
                   removeShadow(n);
                 }
                 highlight[i] = !highlight[i];
                 const entry = document.querySelector(`.dropdown-content a[id='f_${i}']`)
                 if (entry.style.backgroundColor) {
                   entry.style.backgroundColor = null;
                 } else {
                   entry.style.backgroundColor = getColor(i, "60%", "90%");
                 }
                 for (var j = 0; j < highlight.length; j++) {
                   if (highlight[j]) {
                     const col = getColor(j);
                     for (var id of func_map[j]) {
                       var n = document.querySelector(`.node[id='${id}'] ellipse`);
                       addShadow(n, {color:`${col}`});
                     }
                   }
                 }
               }
               // Show the dropdown elements when it's clicked.
               function showDropdown() {
                 document.getElementById("func-list").classList.toggle("show");
               }
               window.onclick = function(event) {
                 if (!event.target.matches('.dropbutton')) {
                   var items = Array.from(document.getElementsByClassName("dropdown-content"));
                   for (var item of items) {
                     item.classList.remove('show');
                   }
                 }
               }
              </script>
              </html>
              </body>
              """)

    return "\n".join(page)