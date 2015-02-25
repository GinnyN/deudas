$(document).on("ready", function(){

	letterLink = $(".link-letter").attr("href");

	$(".change-dates").on("change",function(){
		$(".link-letter").attr("href", letterLink+"?dates="+$(".change-dates").val());
	})

	$(".change-dates").change();

	$(".datepicker").datepicker({
		format: "dd/mm/yyyy"
	});
	$(".modal-click").on("click", clienteClick);
	$('.table').dataTable({
		"language": {
            "url": "//cdn.datatables.net/plug-ins/be7019ee387/i18n/Spanish.json"
        },
        "aoColumnDefs": [
          { "bSortable": false, "aTargets": [ 0 ] } 
          ]
	});
	$(".edit-click").on("click", editClick);
	$(".table").on("draw.dt",bindClicks)
	$("#selectGlosa").on("change",function(){
		$(".loading").addClass("appear");
		$.ajax({
			type: "GET",
			url: "/add/glosa/",
			data: {selectGlosa: $("#selectGlosa").val()},
			success: function(form){
				$(".whereFormGoesGlosa").html(form);
				$(".loading").removeClass("appear");
			}
		})
	})
	$("#interval").on("change",function(){
		if($(this).val()=="anual"){
			date = $("#yearContainer").show();
			date = $("#dateContainer").hide();
		}else{
			date = $("#dateContainer").show();
			date = $("#yearContainer").hide();
		}
	})
	$("#filter, #date, #year, #interval, #activo").on("change",function(){
		if($("#interval").val()=="anual"){
			date = $("#year").val();
			$("#exportExcel").attr("href","/excel/y/"+date+"/");
		}else{
			date = $("#date").val();
			$("#exportExcel").attr("href","/excel/m/"+date+"/")
		}
		if($("#activo").is(":checked")){
			activo = "no-activo"
		}else{
			activo = "activo"
		}
		$(".loading").addClass("appear");
		$.ajax({
			type: "GET",
			url: "/filter/",
			data: {filter: $("#filter").val(), date: date, activo: activo},
			success: function(table){
				tabla = $(".data-table").html(table);
				tabla.find(".table").dataTable({
					"language": {
			            "url": "//cdn.datatables.net/plug-ins/be7019ee387/i18n/Spanish.json"
			        }
				});
				$(".modal-click").on("click", clienteClick);
				$(".edit-click").on("click", editClick);
				$(".table").on("draw.dt",bindClicks);
				$("#masterCheck").on("change", masterCheckFunction);
				$(".controller").on("change", controllerChange);
				$(".loading").removeClass("appear");
			}
		})
	})
	$(".delete").on("click",function(){
		$(".pk").val($(this).data("pk"));
	})
	$(".filter-date").on("click",function(){
		$(".loading").addClass("appear");
		$.ajax({
			type: "GET",
			url: "/load/log/",
			data: {end: $("#a").val(), begin: $("#desde").val(), cliente_pk:$(".cliente_pk").val()},
			success: function(data){
				$("#tab-container").html(data);
				$(".delete").on("click",function(){
					$(".pk").val($(this).data("pk"));
				})
				$(".loading").removeClass("appear");
			}
		})
	})
	$("#deleteClient").on("click", function(){
		var r = confirm("Ésta acción va a borrar todos los datos del cliente, está seguro/a que quiere hacerlo?");
		if (r){
			$(".loading").addClass("appear");
			$.ajax({
				type: "POST",
				url: "/delete/cliente/",
				data: {cliente_pk:$(".cliente_pk").val(), csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val()},
				success: function(data){
					location.reload();
				}
			})
		}
	})

	$(".controller").on("change", controllerChange);

	$("#masterCheck").on("change", masterCheckFunction);

	$("#exportPDF").on("submit", function(event){
		event.preventDefault();
		form = this;
		results = [];
		$.each($("[name=imprimir].checked").serializeArray(), function(){
			results.push($(this).attr("value"));
		})
		if(results.length > 0){
			data = { value: results, csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken").val(), date: $("#date").val(), interval: $("#interval").val() };
			$(".loading").addClass("appear");
			console.log($("#interval").val());
			$.ajax({
				type: "POST",
			  url: $(this).attr("action"),
			  data: data,
			  success: function(data){
			  	generator=window.open('','name','height=400,width=500');
			  	if (generator == undefined){
			  		alert("Por favor Admita Pop Ups en éste dominio y después intente de nuevo");
			  	}else{
			  		generator.document.write(data);
			  		generator.document.close();
			  	}
			  	$(".loading").removeClass("appear");
			  },
			  error: function(data){
			  	console.log(data);
			  	$(".loading").removeClass("appear");
			  }
			});
		}else{
			alert("No hay Clientes seleccionados para crear una carta");
		}
		//$(this).submit();
	})

	$(".removeEventClick").unbind('click.DT');

});

function clienteClick(){
	$(".cliente_pk").val($(this).data("id"));
}

function editClick(){
	$(".loading").addClass("appear");
	$.ajax({
	  type: "GET",
	  url: "/edit/cliente/",
	  data: { pk: $(this).data("id")},
	  success: function(form){
	  	$("#editCliente .modal-body").html(form);
	  	$(".loading").removeClass("appear");
	  }
	})
}

function bindClicks(){
	$(".controller").each(function(){
		if ($("."+$(this).val()).hasClass("checked")){
			$(this).prop("checked",true);
		}else{
			$(this).prop("checked",false);
		}
	})
}

function masterCheckFunction(){
		if($(this).prop("checked")){
			$("[name=imprimir]").addClass("checked");
			$(".controller").prop("checked",true);
		}
		else{
			$("[name=imprimir]").removeClass("checked");
			$(".controller").prop("checked",false);
		}
	}

function controllerChange(){
		if($(this).prop("checked"))
			$("[name=imprimir]."+$(this).val()).addClass("checked");
		else
			$("[name=imprimir]."+$(this).val()).removeClass("checked");
	}