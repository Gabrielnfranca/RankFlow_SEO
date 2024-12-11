import os
import sys
import subprocess
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sync_diagnostics_log.txt')
    ]
)
logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Executa um comando e retorna sua saída"""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            shell=True
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        logger.error(f"Erro ao executar comando {command}: {e}")
        return None, str(e), 1

def check_git_status():
    """Verifica o status do repositório Git"""
    logger.info("Verificando status do Git...")
    stdout, stderr, code = run_command("git status", cwd=os.getcwd())
    
    if code == 0:
        logger.info("Status do Git obtido com sucesso")
        logger.info(stdout)
    else:
        logger.error("Erro ao verificar status do Git")
        logger.error(stderr)

def check_github_remote():
    """Verifica as configurações do repositório remoto"""
    logger.info("Verificando repositório remoto do GitHub...")
    stdout, stderr, code = run_command("git remote -v", cwd=os.getcwd())
    
    if code == 0:
        logger.info("Repositórios remotos:")
        logger.info(stdout)
    else:
        logger.error("Erro ao verificar repositórios remotos")
        logger.error(stderr)

def check_last_commit():
    """Verifica o último commit"""
    logger.info("Verificando último commit...")
    stdout, stderr, code = run_command("git log -1", cwd=os.getcwd())
    
    if code == 0:
        logger.info("Último commit:")
        logger.info(stdout)
    else:
        logger.error("Erro ao verificar último commit")
        logger.error(stderr)

def check_render_deployment():
    """Verifica o status do último deploy no Render"""
    logger.info("Verificando último deploy no Render...")
    # Nota: Este comando é um placeholder. Na prática, você precisaria usar a API do Render
    logger.warning("Verificação do Render requer autenticação na API")

def main():
    logger.info("Iniciando diagnóstico de sincronização")
    logger.info(f"Diretório atual: {os.getcwd()}")
    
    check_git_status()
    check_github_remote()
    check_last_commit()
    check_render_deployment()
    
    logger.info("Diagnóstico concluído")

if __name__ == "__main__":
    main()
