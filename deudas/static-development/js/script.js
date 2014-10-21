$(document).on("ready", function(){
	$(".datepicker").datepicker({
		format: "dd/mm/yyyy"
	});
	$(".modal-click").on("click", clienteClick);
	$('.table').dataTable({
		"language": {
            "url": "//cdn.datatables.net/plug-ins/be7019ee387/i18n/Spanish.json"
        }
	});
	$(".edit-click").on("click", editClick);
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
				$("#tab-container").html(data)
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