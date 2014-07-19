$(document).on("ready", function(){
	$(".datepicker").datepicker({
		format: "dd/mm/yyyy"
	});
	$(".modal-click").on("click",function(){
		console.log("Hola!");
		$(".cliente_pk").val($(this).data("id"));
	});
	$('.table').dataTable({
		"language": {
            "url": "//cdn.datatables.net/plug-ins/be7019ee387/i18n/Spanish.json"
        }
	});
	$(".edit-click").on("click",function(){
		$.ajax({
		  type: "GET",
		  url: "/edit/cliente/",
		  data: { pk: $(this).data("id")},
		  success: function(form){
		  	console.log("Hola!");
		  	$("#editCliente .modal-body").html(form);
		  }
		})
	});
	$("#filter").on("change",function(){
		$.ajax({
			type: "GET",
			url: "/filter/",
			data: {filter: $(this).val()},
			success: function(table){
				$(".data-table").html(table).find(".table").dataTable({
					"language": {
			            "url": "//cdn.datatables.net/plug-ins/be7019ee387/i18n/Spanish.json"
			        }
				});
			}
		})
	})
});