#!/usr/bin/env python3
import secrets
import os
from pathlib import Path
import argparse

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_template():
    """Create a template with all required environment variables"""
    template = {
        'SECRET_KEY': generate_secret_key(),
        'DATABASE_URL': 'sqlite:///instance/task_donegeon.db',
        'LOG_LEVEL': 'INFO',
        'MAX_UPLOAD_SIZE': '16777216',  # 16MB in bytes
        'DATA_PATH': '/var/lib/task_donegeon/data',
        'CONFIG_PATH': '/var/lib/task_donegeon/config',
        'UPLOADS_PATH': '/var/lib/task_donegeon/uploads'
    }
    return template

def save_env_file(env_vars, output_file):
    """Save environment variables to a file"""
    with open(output_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f'{key}={value}\n')

def main():
    parser = argparse.ArgumentParser(description='Generate environment variables for Task Donegeon')
    parser.add_argument('--output', '-o', default='.env',
                      help='Output file (default: .env)')
    parser.add_argument('--print-only', '-p', action='store_true',
                      help='Print to console instead of saving to file')
    parser.add_argument('--regenerate-secret', '-r', action='store_true',
                      help='Regenerate SECRET_KEY even if file exists')
    
    args = parser.parse_args()
    
    # Create env vars
    env_vars = create_env_template()
    
    # If file exists and not regenerating secret, keep existing SECRET_KEY
    if os.path.exists(args.output) and not args.regenerate_secret:
        with open(args.output, 'r') as f:
            for line in f:
                if line.startswith('SECRET_KEY='):
                    env_vars['SECRET_KEY'] = line.strip().split('=')[1]
                    break
    
    if args.print_only:
        print("\nEnvironment Variables for Portainer:")
        print("---------------------------------")
        for key, value in env_vars.items():
            print(f"{key}={value}")
        print("\nCopy these variables into Portainer's environment variables section.")
    else:
        save_env_file(env_vars, args.output)
        print(f"\nEnvironment file saved to: {args.output}")
        print("Make sure to copy these values to Portainer's environment variables section.")
        
    # Print the secret key separately for security
    print("\nYour SECRET_KEY is:")
    print("---------------------------------")
    print(env_vars['SECRET_KEY'])
    print("---------------------------------")
    print("\nMake sure to save this key securely!")

if __name__ == '__main__':
    main() 