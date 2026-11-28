extends Node

const AD_CLIENT := "ca-pub-4437484592938498"
const AD_SLOT := "4315044288"
const CONTAINER_ID := "godot-adsense-container"

var _script_loaded := false
var _script_loading := false

func _ready() -> void:
	if OS.has_feature("web"):
		_load_adsense_library()

func _load_adsense_library() -> void:
	if _script_loaded or _script_loading:
		return

	_script_loading = true

	var document = JavaScriptBridge.get_interface("document")
	var script = document.createElement("script")
	script.async = true
	script.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + AD_CLIENT
	script.crossOrigin = "anonymous"

	# Optional: know when it finished loading
	script.onload = JavaScriptBridge.create_callback(_on_adsense_loaded)

	document.head.appendChild(script)

func _on_adsense_loaded(args) -> void:
	_script_loaded = true
	_script_loading = false
	print("AdSense library loaded")

func show_ad() -> void:
	if not OS.has_feature("web"):
		return

	if not _script_loaded:
		push_warning("AdSense library not loaded yet")
		return

	hide_ad()

	var document = JavaScriptBridge.get_interface("document")

	var container = document.createElement("div")
	container.id = CONTAINER_ID
	container.style.position = "fixed"
	container.style.bottom = "0"
	container.style.left = "0"
	container.style.width = "100%"
	container.style.zIndex = "1000"
	container.style.textAlign = "center"

	var ins = document.createElement("ins")
	ins.className = "adsbygoogle"
	ins.style.display = "block"
	ins.setAttribute("data-ad-client", AD_CLIENT)
	ins.setAttribute("data-ad-slot", AD_SLOT)
	ins.setAttribute("data-ad-format", "auto")
	ins.setAttribute("data-full-width-responsive", "true")

	container.appendChild(ins)
	document.body.appendChild(container)

	JavaScriptBridge.eval("(window.adsbygoogle = window.adsbygoogle || []).push({});")

func hide_ad() -> void:
	if not OS.has_feature("web"):
		return

	var document = JavaScriptBridge.get_interface("document")
	var existing = document.getElementById(CONTAINER_ID)
	if existing:
		existing.remove()
