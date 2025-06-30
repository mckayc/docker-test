#!/usr/bin/env python3
import click
import subprocess
import datetime
import os
import shutil
from pathlib import Path

BACKUP_DIR = Path('backups')
VOLUMES = ['task_donegeon_data', 'task_donegeon_config', 'task_donegeon_uploads']

def run_command(command):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running command: {e.stderr}", err=True)
        raise click.Abort()

@click.group()
def cli():
    """Task Donegeon Management CLI"""
    BACKUP_DIR.mkdir(exist_ok=True)

@cli.command()
@click.option('--name', help='Backup name (default: timestamp)')
def backup(name):
    """Backup all Docker volumes"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = name or f'backup_{timestamp}'
    backup_path = BACKUP_DIR / backup_name
    backup_path.mkdir(exist_ok=True)

    click.echo("Stopping containers...")
    run_command('docker compose down')

    for volume in VOLUMES:
        click.echo(f"Backing up {volume}...")
        temp_container = f'backup_{volume}'
        
        # Create a temporary container with volume mounted
        run_command(f'docker run -v {volume}:/source:ro '
                   f'--name {temp_container} debian:latest tail -f /dev/null &')
        
        try:
            # Copy data from volume
            run_command(f'docker cp {temp_container}:/source/. "{backup_path / volume}"')
        finally:
            # Cleanup
            run_command(f'docker rm -f {temp_container}')

    click.echo(f"Backup completed: {backup_path}")
    click.echo("Starting containers...")
    run_command('docker compose up -d')

@cli.command()
@click.argument('backup_name')
def restore(backup_name):
    """Restore Docker volumes from backup"""
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        raise click.BadParameter(f"Backup '{backup_name}' not found")

    click.echo("Stopping containers...")
    run_command('docker compose down')

    for volume in VOLUMES:
        click.echo(f"Restoring {volume}...")
        volume_path = backup_path / volume
        if not volume_path.exists():
            click.echo(f"Warning: No backup found for {volume}", err=True)
            continue

        temp_container = f'restore_{volume}'
        
        # Create a temporary container with volume mounted
        run_command(f'docker run -v {volume}:/target '
                   f'--name {temp_container} debian:latest tail -f /dev/null &')
        
        try:
            # Copy data to volume
            run_command(f'docker cp "{volume_path}/." {temp_container}:/target/')
        finally:
            # Cleanup
            run_command(f'docker rm -f {temp_container}')

    click.echo("Restore completed")
    click.echo("Starting containers...")
    run_command('docker compose up -d')

@cli.command()
def list_backups():
    """List available backups"""
    if not BACKUP_DIR.exists():
        click.echo("No backups found")
        return

    backups = [d for d in BACKUP_DIR.iterdir() if d.is_dir()]
    if not backups:
        click.echo("No backups found")
        return

    click.echo("\nAvailable backups:")
    for backup in backups:
        size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
        click.echo(f"- {backup.name} ({size/1024/1024:.1f} MB)")

@cli.command()
@click.argument('backup_name')
def remove_backup(backup_name):
    """Remove a backup"""
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        raise click.BadParameter(f"Backup '{backup_name}' not found")

    shutil.rmtree(backup_path)
    click.echo(f"Backup '{backup_name}' removed")

if __name__ == '__main__':
    cli() 