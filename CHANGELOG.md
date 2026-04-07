# Changelog

## [3.0.0](https://github.com/viru185/AutoUFL/compare/v2.0.0...v3.0.0) (2026-04-07)


### ⚠ BREAKING CHANGES

* **muri:** implement ExcelProcessor for handling Excel files and converting month names to dates
* **muri:** add client configuration for sheet processing and tag mapping
* **muri:** add initial __init__.py file for the muri client

### Features

* **base_processor:** add method to retrieve sheet names from Excel files using regex matching ([faf6f05](https://github.com/viru185/AutoUFL/commit/faf6f0568bf4c0cae68d195aecbe3448067d40fa))
* **muri:** add client configuration for sheet processing and tag mapping ([445419b](https://github.com/viru185/AutoUFL/commit/445419b17a9140c1bbac45fa179240c8e27dec3c))
* **muri:** add initial __init__.py file for the muri client ([d06749a](https://github.com/viru185/AutoUFL/commit/d06749ad01ef6ad3c77ec9667fc2fc529d65de9f))
* **muri:** implement ExcelProcessor for handling Excel files and converting month names to dates ([69ee17c](https://github.com/viru185/AutoUFL/commit/69ee17c7287d91b8692158b5263f20b38b5fba4e))


### Bug Fixes

* rename COLUMNS_TO_DRIP_RE_EXPRESSION to COLUMNS_TO_DROP_RE_EXPRESSION in client configurations and processors ([2958b29](https://github.com/viru185/AutoUFL/commit/2958b294b98f0dd0f8b67f79db1284004664287d))

## [2.0.0](https://github.com/viru185/AutoUFL/compare/v1.0.0...v2.0.0) (2026-04-07)


### ⚠ BREAKING CHANGES

* **mahan:** implement ExcelProcessor for handling Excel files and generating normalized CSVs for `mahan` client
* **mahan:** add client configuration for sheet processing and tag mapping
* **mahan:** add initial implementation of the Mahan client

### Features

* **config:** add boolean env parser and logging configuration controls ([c418ad3](https://github.com/viru185/AutoUFL/commit/c418ad312d374fcaef832a901d2bc1b8abca24d4))
* **logger:** add configurable logging formats with rotation and retention ([910fcf3](https://github.com/viru185/AutoUFL/commit/910fcf3986ad3aef2357ac64ddfb7812aa75794c))
* **mahan:** add client configuration for sheet processing and tag mapping ([774ffe2](https://github.com/viru185/AutoUFL/commit/774ffe25c714755705fb033f1493b125976ed050))
* **mahan:** add initial implementation of the Mahan client ([70d0910](https://github.com/viru185/AutoUFL/commit/70d0910358e6b1cefa0347689b911492cd14d832))
* **mahan:** implement ExcelProcessor for handling Excel files and generating normalized CSVs for `mahan` client ([4d4251e](https://github.com/viru185/AutoUFL/commit/4d4251e76a3fb8289ada78ddec3fd7d7d0aecb19))
* **watcher:** add detailed logging for file processing lifecycle ([05d0c29](https://github.com/viru185/AutoUFL/commit/05d0c298b893757308c5fe4313ec7f01f501ebf6))


### Bug Fixes

* **baseProcessor:** streamline DataFrame operations, fix column insert and improve readability, ([9e226e8](https://github.com/viru185/AutoUFL/commit/9e226e82afb77ccf13bb2fccb89c342b3b397ef6))
* **config:** ensure LOG_RETENTION is parsed as an integer ([de01aa9](https://github.com/viru185/AutoUFL/commit/de01aa96b0a7f5deb7851bd3c1c1f1ab526e8e3d))
* **processor:** correct output file path handling in process_file method ([df0b2e5](https://github.com/viru185/AutoUFL/commit/df0b2e5df9715669f5339e08af54cceade2e0099))
* **processor:** update process_file method to correctly handle output file path and save UFL CSV ([8c7913d](https://github.com/viru185/AutoUFL/commit/8c7913d40d599bc10cb39cd4e036c5f0ea1020e4))


### Documentation

* **env:** provide complete environment variable template ([c7c8ed5](https://github.com/viru185/AutoUFL/commit/c7c8ed5ad352270c3632d7fc778ccea3cd6b3e7f))
* **readme:** expand documentation with usage, config, and onboarding guide ([c7cedd4](https://github.com/viru185/AutoUFL/commit/c7cedd49329c3844b4ab8058d5d76eb38b056423))
* **uv:** version change in file. ([0953ffd](https://github.com/viru185/AutoUFL/commit/0953ffd1d43ac4a4ea15f4b47a0a96ecd01f2998))

## [1.0.0](https://github.com/viru185/AutoUFL/compare/v0.2.0...v1.0.0) (2026-04-03)


### ⚠ BREAKING CHANGES

* 
* **init:** dynamic import of the processor module based on environment variable.

### Features

* add config for the client one. ([974e208](https://github.com/viru185/AutoUFL/commit/974e2081825cdbb674ad8f20eb862fe1781184b9))
* **build:** add script to automate building for multiple clients ([859ba21](https://github.com/viru185/AutoUFL/commit/859ba213c49c153ba876116fe2d0e30c3a25e946))
* **build:** implement manifest-based multi-client build pipeline ([37b3b5e](https://github.com/viru185/AutoUFL/commit/37b3b5e0add9daf674f21ee282a896caaf17259b))
* **ci:** add GitHub Actions workflow for test build and release process ([4268f61](https://github.com/viru185/AutoUFL/commit/4268f6166d8acec13dd42a253b3f7599ac02bc80))
* **ci:** enhance GitHub Actions workflow to support multiple client environments ([8020b1d](https://github.com/viru185/AutoUFL/commit/8020b1d1c6ca18aef892459f15746174df3883bb))
* **cli:** add client selection flag for runtime execution ([98f91e2](https://github.com/viru185/AutoUFL/commit/98f91e2f136d816048697be19e97485bc9040379))
* **client:** add utkal client configuration for sheet processing and tag mapping ([dcfe4be](https://github.com/viru185/AutoUFL/commit/dcfe4be7f7c4b26643044bdf806bec821c5a6fe9))
* **clients:** introduce manifest-driven client registry ([f8e32ef](https://github.com/viru185/AutoUFL/commit/f8e32efcdbd3d4a3e7288824b69aefae944eab0b))
* **config:** enhance base path retrieval for frozen applications ([859ba21](https://github.com/viru185/AutoUFL/commit/859ba213c49c153ba876116fe2d0e30c3a25e946))
* **init:** dynamic import of the processor module based on environment variable. ([e1c544b](https://github.com/viru185/AutoUFL/commit/e1c544b136b998dda9dd0b18baab7c261677c4f9))
* **processor:** add baseExcelProcessor class for Excel file processing with regex column filtering and CSV output, will be common for all the client ([8db8e74](https://github.com/viru185/AutoUFL/commit/8db8e743d9e3fc613c1a30c5d226eddbb1bf077c))
* **processor:** add method to rename dataframe columns using a mapping dictionary ([cecb011](https://github.com/viru185/AutoUFL/commit/cecb011f9ee3c334fcda235933c872817b6f21df))
* **processor:** implement ExcelProcessor class for for utkal site processing Excel files and generating UFL CSV output ([2f62103](https://github.com/viru185/AutoUFL/commit/2f62103c0376ed046c9058acba989dd4bca561a6))
* **processor:** implement ExcelProcessor class for processing Excel files and generating UFL CSV output for client_one ([c4b0523](https://github.com/viru185/AutoUFL/commit/c4b0523ab84d971abe60a2eb7ad9dddc26ee24a4))
* release manifest-driven multi-client build system with automated CI/CD pipeline ([7d4bea2](https://github.com/viru185/AutoUFL/commit/7d4bea2fbb18fd7a84af9f014da03d2c28ff0c7a))
* **utkal:** add initial implementation of Utkal client module ([92c9b96](https://github.com/viru185/AutoUFL/commit/92c9b96c3a5d7c4a183c6daa4af93144569e3b11))


### Bug Fixes

* **config:** default timestamp format. ([5847e0c](https://github.com/viru185/AutoUFL/commit/5847e0c78f37190829617051782a506fbfb56269))
* **config:** LOG_TO_CONSOLE constant is set to bool. ([f0b7bbe](https://github.com/viru185/AutoUFL/commit/f0b7bbe880854470be79301c39cb5739e3d267bc))
* **config:** rename config file with client_config for each config to separate from app config file ([d5cdc38](https://github.com/viru185/AutoUFL/commit/d5cdc384b02802b5fb3579e38298bddaf58bea8b))
* **config:** resolve input and output directory path ([708943f](https://github.com/viru185/AutoUFL/commit/708943fd16e65b1d17cece5c7bc1815a2abf0257))
* **config:** update ISO timestamp format to use underscore separator ([2b54de3](https://github.com/viru185/AutoUFL/commit/2b54de3ac560f8aef7cabe0473e919ef065460a0))
* **config:** update sheets to process, add regex for column filtering, and move tag mapping to site specific ([1671a10](https://github.com/viru185/AutoUFL/commit/1671a10c665fb675c8a4c1901fbec051e145d0f7))
* **dependencies:** add openpyxl dependency for Excel file processing ([96fe48c](https://github.com/viru185/AutoUFL/commit/96fe48cd512ac9f8a64296c1f7b9c2272dd18f4e))
* **dependencies:** remove unused dependencies openpyxl and typer from project ([e30b529](https://github.com/viru185/AutoUFL/commit/e30b5295be240c57493c0fd11ea7655b20468324))
* **init:** log client loading information for 'all' clients ([859ba21](https://github.com/viru185/AutoUFL/commit/859ba213c49c153ba876116fe2d0e30c3a25e946))
* **init:** remove unused ProcessingError from client module exports ([e0288de](https://github.com/viru185/AutoUFL/commit/e0288de612445e9b5400af9c5554e4c50067fbc9))
* **logger:** now logger will alway use log file next executable. ([554c6bf](https://github.com/viru185/AutoUFL/commit/554c6bf12557438852ccf4d882229245b003a559))
* **watcher:** change the logic of the file, remove repeated code logic ([ca5f567](https://github.com/viru185/AutoUFL/commit/ca5f5672c15ff7001ab4b887a071ea12718d1a94))
* **watcher:** specify return type for _rename method ([859ba21](https://github.com/viru185/AutoUFL/commit/859ba213c49c153ba876116fe2d0e30c3a25e946))
* **watcher:** update timestamp generation to use current datetime format ([41f3ae2](https://github.com/viru185/AutoUFL/commit/41f3ae2af32870d500bc85c8201097b800a109c5))
* **watcher:** update timestamp generation to use ISO format and improve error logging ([42a63a3](https://github.com/viru185/AutoUFL/commit/42a63a3f8372d50b87b4e332503fdec0de78198d))

## [0.2.0](https://github.com/viru185/AutoUFL/compare/v0.1.1...v0.2.0) (2026-03-30)


### Features

* **build,release:** fix metadata handling, bundle toml, and improve build workflow ([6f17a2b](https://github.com/viru185/AutoUFL/commit/6f17a2b6b4b97694151d469b650298787bccd833))

## [0.1.1](https://github.com/viru185/AutoUFL/compare/v0.1.0...v0.1.1) (2026-03-30)


### Bug Fixes

* realease workflow, will add the tag and attach exe file. ([a093a13](https://github.com/viru185/AutoUFL/commit/a093a13f3d97dbb3aad00db5a1043b4c6ce9d53a))

## 0.1.0 (2026-03-30)


### Features

* add CLI flags, timestamp config, metadata, docs, and release workflow ([2ab7860](https://github.com/viru185/AutoUFL/commit/2ab786085172e4805bdcad9f8b0552fc3c53cfbd))
* Add Excel processing functionality with logging and folder monitoring ([987cc89](https://github.com/viru185/AutoUFL/commit/987cc893b013e3945ad31feaaa50ee0f9274586b))
* Add main.spec for PyInstaller configuration ([1363214](https://github.com/viru185/AutoUFL/commit/1363214bb4fa7d3debfe2f72aa0376e7fa8f0067))
* Add openpyxl dependency and enhance Excel processing with header normalization ([82bccc3](https://github.com/viru185/AutoUFL/commit/82bccc3eeafef2c9f8c22757ad9e9e39a000b383))
* Add python-dotenv dependency and update configuration to load environment variables ([41e6384](https://github.com/viru185/AutoUFL/commit/41e6384c8bebc7bcf63607006573106b2864e043))
* enhance CLI styling, metadata handling, timestamp processing, and release readiness ([dfc9da2](https://github.com/viru185/AutoUFL/commit/dfc9da20275624887ed17f4f0b1b10dd29caccfa))
* trigger release ([9c79c31](https://github.com/viru185/AutoUFL/commit/9c79c31947e020b55ce95270789ccc1a41a11dd6))


### Bug Fixes

* add V to version ([9b0ed87](https://github.com/viru185/AutoUFL/commit/9b0ed87b9a16a8178be88d8fd4ab6c1a16bf6bb0))
* change logs from debug to info ([991cf0f](https://github.com/viru185/AutoUFL/commit/991cf0f575d14338665c55b8f81622d5a23d2954))
* ignore type error with comment. ([89218cc](https://github.com/viru185/AutoUFL/commit/89218cc084829053aa124b5a7a55a08a6db31bf9))
* strong type checking. ([70675b4](https://github.com/viru185/AutoUFL/commit/70675b416e652e14348d399b66db552ec468324b))
* typo in the code ([336ceeb](https://github.com/viru185/AutoUFL/commit/336ceeb5a1ba1e0d22426650ac557e7894ba4fef))
* Update .gitignore to include .env file and ensure proper formatting ([f532374](https://github.com/viru185/AutoUFL/commit/f53237432377b6b848e02401ef5596a2eb70def3))
* Update default log level to INFO and enhance value cleaning in Excel processing ([90a417e](https://github.com/viru185/AutoUFL/commit/90a417e15bde474436202748a526fb2262467e4e))
* update github action workflow ([a26e6ae](https://github.com/viru185/AutoUFL/commit/a26e6aedb1f9da427f8b0bad8915dd33cb04229a))
