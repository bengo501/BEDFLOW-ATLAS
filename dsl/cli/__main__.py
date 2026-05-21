# permite python m cli a partir da pasta dsl com sys path correcto
import sys

from cli.app import dispatch_main
from graceful_shutdown import install_graceful_shutdown

if __name__ == "__main__":
    install_graceful_shutdown("pt")
    try:
        sys.exit(dispatch_main())
    except KeyboardInterrupt:
        from graceful_shutdown import exit_on_user_interrupt

        exit_on_user_interrupt()
