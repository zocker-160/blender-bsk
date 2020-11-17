ADDON_DIR=./src
ZIP_NAME="BSK-Blender_01.zip"

addon:
	mkdir -p ${ADDON_DIR}/addon/io_scene_bsk
	cp ${ADDON_DIR}/*.py ${ADDON_DIR}/addon/io_scene_bsk/
	cd ${ADDON_DIR}/addon/ && zip -r ${ZIP_NAME} io_scene_bsk/
	mv ${ADDON_DIR}/addon/${ZIP_NAME} .
	rm -rf ${ADDON_DIR}/addon
clean:
	rm -rf ${ADDON_DIR}/addon
