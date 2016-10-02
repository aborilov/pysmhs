var baseUrlGet = "/get?action=";
var actionGetJson = "getJson";
var getDataObj = new getData(baseUrlGet,receiveJson,"json","get",undefined,undefined);
var tags = null;
var inkscapeNS = "http://www.inkscape.org/namespaces/inkscape";
var scripted = false;
var sendData = [];
var empty = true;
var currMap = {};

function receiveJson(json){
	tags = eval ("(" + json + ")");
}
function hello(){
	alert("hello");
}

function sendTags(){
	if (empty){
		return;
	}
	var xmlhttp;
	if (window.XMLHttpRequest)
	{// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp=new XMLHttpRequest();
	}
	else
	{// code for IE6, IE5
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	}

	xmlhttp.open("POST","/get",true);
	xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlhttp.send(sendData.join("&"));
	sendData = [];
	empty = true;
}

function setTag(tagName,value){
	empty = false;
//	eval('sendData.'+tagName+'="'+value+'"');
	sendData.push(tagName+"="+value);
	sendTags();
}

function getStyleParam(style,paramName){
	var styleParams = style.split(";");
	for (var p=0;p<styleParams.length;p++){
		var fillParams = styleParams[p].split(":");
		if (fillParams[0]==paramName){
			return fillParams[1];
		}
	}
	return null;
}

function getNextColor(style,colors){
	var colorsList = colors.split("/");
	if (colorsList.length>1){
		var currentColor = getStyleParam(style, "fill");
		if (currentColor!=null){
			for (var i=0;i<colorsList.length;i++){
				if (colorsList[i]==currentColor){
					if (i<colorsList.length-1)
						return colorsList[i+1];
					else
						return colorsList[0];
				}
			}
			return colorsList[0];
		}else
			return colorsList[0];
	}else{
		return colors;
	}
}

function changeStyleParam(currentStyle,paramName,value){
	var styleParams = currentStyle.split(";");
	for (var p=0;p<styleParams.length;p++){
		var fillParams = styleParams[p].split(":");
		if (fillParams[0]==paramName){
			fillParams[1] = value;
			styleParams[p] = fillParams.join(":");
		}
	}
	return styleParams.join(";");
}

function getTag(name){
	if (tags!=null){
		return eval('tags.tags.'+name);
	}
	return null;
}

function getMapValue(map,name){
	if (map!=null){
	
		if (name.indexOf('%')==0){
			name = name.slice(1);
			return eval('map.'+name);
		}
	}
	return name;
}

function  replacer(str){
str = str.replace(/\'/g,"");
return "\'"+getMapValue(currMap,str)+"\'";
}

function goThroughNodes(svg,map){
	if (map==null) map = { };
	var nodes = svg.childNodes;
	var l = nodes.length;
	var json = {};
	for (var j=0;j<l;j++){
		var element = nodes[j];
		if (element.nodeType==1){
			var label = element.getAttributeNS(inkscapeNS,"label");
//			alert(label);
			if (label!=null && label.length>0){
				try {
					json = eval ("{[" + label + "]}");
					for (var p=0;p<json.length;p++){
						if (json[p].attr=="color"){
							var list = json[p].list;
							for (var i=0;i<list.length;i++){
								var tag = list[i].tag;
								tag = getMapValue(map, tag);
								var data = getTag(tag);
								if (data!=null){
									if(list[i].data==data){
										var style = element.getAttribute("style");
										element.setAttributeNS(null, "style",changeStyleParam(style,"fill",getNextColor(style, list[i].param)));
									}
								}
							}
						}else if (json[p].attr=="clone"){
							for (var i=0;i<json[p].map.length;i++){
								var mapSplit = json[p].map[0].split("=");
								eval('map.'+mapSplit[0].slice(1)+'="'+mapSplit[1]+'"');
							}
						}else if (json[p].attr=="script" && !scripted) {
							element.setAttributeNS(null,"cursor","pointer");
							var list = json[p].list;
							var reg = new RegExp("\'(%\\w+)\'", "g");
							for (var i=0;i<list.length;i++){
								if (reg.test(list[i].param)){
									currMap = map;
									//alert(list[i].param.replace(reg,replacer));
									element.setAttributeNS(null,"on"+list[i].evt,list[i].param.replace(reg,replacer));
								}else{
									currMap = map;
									element.setAttributeNS(null,"on"+list[i].evt,list[i].param);
								}
							}
						}else if (json[p].attr=="get") {
							element.childNodes[0].childNodes[0].nodeValue=getTag(getMapValue(map, json[p].tag));
						}else if (json[p].attr=="set" && !scripted) {
							element.setAttributeNS(null,"cursor","pointer");
							if (json[p].type=="Variable")
								element.setAttributeNS(null,"onclick","top.setTag('"+json[p].tag+"','"+getTag(json[p].src)+"')");
							else
								element.setAttributeNS(null,"onclick","top.setTag('"+json[p].tag+"','"+json[p].src+"')");
						}else if (json[p].attr=="bar") {
							if (!scripted)
								element.setAttributeNS(inkscapeNS,"height",element.getAttribute("height"));
							var data = getTag(getMapValue(map,json[p].tag));
							if (data>=json[p].min){
								var h = element.getAttributeNS(inkscapeNS,"height");
								var proc = (100/(json[p].max-json[p].min))*(data-json[p].min);
								element.setAttributeNS(null,"height",(h/100)*proc);
							}else
								element.setAttributeNS(null,"height",0);

						}
					}
				}catch (e) {
					// alert(e);
				}
				if (element.nodeName=="g"){
					goThroughNodes(element,map);
				}
			}
		}
	}
}

function init(){
	thread();
}

function thread(){
	var svgHolder = document.getElementById('svgHolder');
	getDataObj.url=baseUrlGet+actionGetJson;
	getDataObj.getData();
	if (tags!=null){
		for (var i=0;i<svgHolder.childNodes.length;i++){
			if(svgHolder.childNodes[i].nodeName=="EMBED"){
				goThroughNodes(svgHolder.childNodes[i].getSVGDocument().childNodes[1],null);
				scripted=true;
			}
		}
	}
	doTimer();
}

function doTimer() {
	setTimeout("thread()",100);
}
