#!/usr/bin/env python3
from app import create_app
from config import ProductionConfig

application = create_app(config_class=ProductionConfig)

if __name__ == "__main__":
    application.run()
