$(document).on("ready", function(){
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
		$.ajax({
			type: "GET",
			url: "/add/glosa/",
			data: {selectGlosa: $("#selectGlosa").val()},
			success: function(form){
				$(".whereFormGoesGlosa").html(form);
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
		$.ajax({
			type: "GET",
			url: "/filter/",
			data: {filter: $("#filter").val(), date: date, activo: activo},
			success: function(table){
				$(".data-table").html(table).find(".table").dataTable({
					"language": {
			            "url": "//cdn.datatables.net/plug-ins/be7019ee387/i18n/Spanish.json"
			        }
				});
				$(".modal-click").on("click", clienteClick);
				$(".edit-click").on("click", editClick);
				$(".table").on("draw.dt",bindClicks)
			}
		})
	})
	$(".delete").on("click",function(){
		$(".pk").val($(this).data("pk"));
	})
	$(".filter-date").on("click",function(){
		$.ajax({
			type: "GET",
			url: "/load/log/",
			data: {end: $("#a").val(), begin: $("#desde").val(), cliente_pk:$(".cliente_pk").val()},
			success: function(data){
				console.log("Hola!");
				$("#tab-container").html(data);
				$(".delete").on("click",function(){
					$(".pk").val($(this).data("pk"));
				})
			}
		})
	})
	$("#deleteClient").on("click", function(){
		var r = confirm("Ésta acción va a borrar todos los datos del cliente, está seguro/a que quiere hacerlo?");
		if (r){
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

	$(".controller").on("change",function(){
		if($(this).prop("checked"))
			$("[name=imprimir]."+$(this).val()).addClass("checked");
		else
			$("[name=imprimir]."+$(this).val()).removeClass("checked");
	})

	$("#masterCheck").on("change",function(){
		if($(this).prop("checked")){
			$("[name=imprimir]").addClass("checked");
			$(".controller").prop("checked",true);
		}
		else{
			$("[name=imprimir]").removeClass("checked");
			$(".controller").prop("checked",false);
		}
	});

	$("#exportPDF").on("submit", function(event){
		event.preventDefault();
		form = this;
		results = [];
		$.each($("[name=imprimir].checked").serializeArray(), function(){
			results.push($(this).attr("value"));
		})
		if(results.length > 0){
			data = { value: results, csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken").val() };
			console.log(data);
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
			  },
			  error: function(data){
			  	console.log(data);
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
	$.ajax({
	  type: "GET",
	  url: "/edit/cliente/",
	  data: { pk: $(this).data("id")},
	  success: function(form){
	  	$("#editCliente .modal-body").html(form);
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