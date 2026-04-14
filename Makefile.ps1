param(
    [string]$cmd = "help"
)

$VENV = "venv"

function Ensure-Venv {
    if (!(Test-Path "$VENV")) {
        python -m venv $VENV
    }
}

function Activate-Venv {
    & "$VENV\Scripts\Activate.ps1"
}

switch ($cmd) {
    "install" {
        Ensure-Venv
        Activate-Venv
        python -m pip install --upgrade pip
        pip install pywin32 PyQt5 win10toast requests
    }
    "run" {
        Ensure-Venv
        Activate-Venv
        python main_loop.py
    }
    "test" {
        Ensure-Venv
        Activate-Venv
        python test_parser.py
    }
    "clean" {
        Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
        Remove-Item -Force bugs.json -ErrorAction SilentlyContinue
    }
    default {
        echo "use: .\Makefile.ps1 install|run|test|clean"
    }
}

