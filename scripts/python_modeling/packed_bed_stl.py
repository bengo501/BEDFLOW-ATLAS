#!/usr/bin/env python3
# este arquivo e apenas um wrapper de linha de comando
# ele nao contem a logica pesada de geometria
# toda a geometria e validacao ficam no modulo pure generation
# o motivo deste wrapper e simples
# o bed wizard e o backend chamam um script fixo
# por isso este script fornece uma interface estavel

from __future__ import annotations

# argparse e o modulo padrao para ler argumentos da linha de comando
import argparse

# sys e usado para ajustar o caminho de importacao
# isso garante que os imports funcionem mesmo quando o cwd muda
import sys

# Path e usado para lidar com caminhos de forma segura
from pathlib import Path

# primeira acao
# colocamos o diretorio deste arquivo no sys path
# assim o python encontra pure generation e outros modulos no mesmo diretorio
_PMDIR = Path(__file__).resolve().parent
if str(_PMDIR) not in sys.path:
    sys.path.insert(0, str(_PMDIR))

# segunda acao
# importamos o que o script precisa
# we mantemos alguns simbolos comecando com underscore porque testes importam eles
from pure_generation import (  # noqa: E402
    _packing_method_name,
    _to_float,
    _to_int,
    generate_packed_bed_stl,
    load_bed_json,
)


def main() -> None:
    # esta funcao e o ponto de entrada quando o script e executado
    # ela cria um parser de argumentos
    ap = argparse.ArgumentParser(description="gera stl empacotado python sem blender")

    # bed json e a configuracao de entrada
    # este json contem parametros do cilindro e da geracao
    ap.add_argument("bed_json", type=Path, help="ficheiro bed json")

    # out stl e o destino do arquivo stl gerado
    ap.add_argument("out_stl", type=Path, help="ficheiro stl saida")

    # max passos e usado apenas pelo modo legacy rigid body
    # nos modos scientific spherical e hexagonal nao e necessario
    ap.add_argument(
        "--max-passos",
        type=int,
        default=12000,
        help="passos simulacao apenas no modo rigid body legacy",
    )
    ap.add_argument(
        "--progress",
        action="store_true",
        help="abre janela com barra de progresso (por defeito auto no terminal)",
    )
    ap.add_argument(
        "--no-progress",
        action="store_true",
        help="desativa janela de progresso",
    )

    # parse args transforma os valores digitados no terminal em um objeto
    args = ap.parse_args()

    # valida se o arquivo de entrada existe
    if not args.bed_json.exists():
        # raise SystemExit e o jeito padrao de parar com codigo de erro
        raise SystemExit(f"ficheiro nao encontrado: {args.bed_json}")

    # chamada principal
    # aqui delegamos para pure generation
    # ele vai ler o json
    # escolher o modo de empacotamento
    # validar e depois exportar stl
    pw = False if args.no_progress else (True if args.progress else None)
    generate_packed_bed_stl(
        args.bed_json,
        args.out_stl,
        max_passos=args.max_passos,
        progress_window=pw,
    )

    # mensagem final para o usuario
    print(f"[ok] stl escrito: {args.out_stl}")


if __name__ == "__main__":
    # esta condicao garante que main so roda quando o arquivo e executado direto
    main()
