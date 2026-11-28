extends Node

const AD_CLIENT := "ca-pub-4437484592938498"
const AD_SLOT := "4315044288"
const CONTAINER_ID := "godot-adsense-container"

var _script_loaded := false

func _ready() -> void:
	if OS.has_feature("web"):
		_load_adsense_library()

func _load_adsense_library() -> void:
	if _script_loaded:
		return
	
	var document = JavaScriptBridge.get_interface("document")
	var script = document.createElement("script")
	script.async = true
	script.src = "https://googlesyndication.com" + AD_CLIENT
	script.crossOrigin = "anonymous"
	document.head.appendChild(script)
	
	_script_loaded = true

func show_ad() -> void:
	if not OS.has_feature("web"):
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
