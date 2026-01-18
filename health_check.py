#!/usr/bin/env python3
"""
health_check.py

Script para realizar checklist automatizado de saúde (ping, DNS, porta TCP) em uma lista de hosts.

Este script lê um arquivo de entrada contendo uma coluna de hosts (nomes ou endereços IP). Para cada host,
executa as seguintes verificações:
- ping ICMP para verificar disponibilidade de rede;
- resolução DNS (para nomes de host) usando socket.gethostbyname;
- teste de conexão TCP em uma porta (por padrão 80).

O resultado é exportado para um CSV com colunas: host, ping_status, dns_status, port_status.

Uso:
    python health_check.py --input hosts.txt --output results.csv --port 80

Parâmetros:
    --input: caminho para o arquivo de entrada (hosts separados por linha).
    --output: arquivo CSV de saída (default: healthcheck_<data>.csv).
    --port: porta TCP a testar (default: 80).
    --timeout: timeout em segundos para conexões (default: 2).
    --encoding: encoding do arquivo de entrada (default: utf-8).

Criado em 2026-01-18.
"""

import argparse
import csv
import platform
import socket
import subprocess
from datetime import datetime


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checklist de saúde de hosts (ping/DNS/porta)")
    parser.add_argument("--input", "-i", required=True, help="Arquivo de entrada com lista de hosts")
    parser.add_argument("--output", "-o", help="Arquivo CSV de saída (default: healthcheck_<data>.csv)")
    parser.add_argument("--port", "-p", type=int, default=80, help="Porta TCP para teste (default: 80)")
    parser.add_argument("--timeout", "-t", type=int, default=2, help="Timeout em segundos para testes")
    parser.add_argument("--encoding", "-e", default="utf-8", help="Encoding do arquivo de entrada")
    return parser.parse_args()


def check_ping(host, timeout):
    # Usa comando ping nativo dependendo do sistema operacional
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", "-w", str(timeout), host]
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def check_dns(host):
    try:
        socket.gethostbyname(host)
        return True
    except socket.error:
        return False


def check_tcp_port(host, port, timeout):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def read_hosts(path, encoding):
    hosts = []
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            h = line.strip()
            if h:
                hosts.append(h)
    return hosts


def write_results(results, output_path):
    fieldnames = ["host", "ping_status", "dns_status", "port_status"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def main():
    args = parse_arguments()
    output = args.output
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"healthcheck_{timestamp}.csv"
    hosts = read_hosts(args.input, args.encoding)
    results = []
    for host in hosts:
        ping_ok = check_ping(host, args.timeout)
        dns_ok = check_dns(host)
        port_ok = check_tcp_port(host, args.port, args.timeout)
        results.append({
            "host": host,
            "ping_status": "OK" if ping_ok else "FAIL",
            "dns_status": "OK" if dns_ok else "FAIL",
            "port_status": "OK" if port_ok else "FAIL",
        })
    write_results(results, output)
    print(f"Resultados exportados para: {output}")


if __name__ == "__main__":
    main()
