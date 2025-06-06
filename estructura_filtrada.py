import os

IGNORAR_DIRS = {
    '.git', '__pycache__', 'migrations', '.venv', 'env', 'venv', 'node_modules'
}
EXT_PERMITIDAS = {'.py', '.html', '.js', '.css', '.txt', '.json', '.md'}

def es_ignorado(nombre):
    return nombre in IGNORAR_DIRS

def extension_valida(nombre):
    return any(nombre.endswith(ext) for ext in EXT_PERMITIDAS)

with open("estructura_filtrada.txt", "w", encoding="utf-8") as f:
    for root, dirs, files in os.walk("."):
        # Ignora directorios innecesarios
        dirs[:] = [d for d in dirs if not es_ignorado(d)]

        nivel = root.replace(os.getcwd(), "").count(os.sep)
        indent = "    " * nivel
        nombre_dir = os.path.basename(root)
        f.write(f"{indent}{nombre_dir}/\n")

        for archivo in files:
            if extension_valida(archivo):
                subindent = "    " * (nivel + 1)
                f.write(f"{subindent}{archivo}\n")
