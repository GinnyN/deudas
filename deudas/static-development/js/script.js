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
	$("#filter, #date").on("change",function(){
		$.ajax({
			type: "GET",
			url: "/filter/",
			data: {filter: $("#filter").val(), date: $("#date").val()},
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
});

function clienteClick(){
	console.log("Hola!");
	$(".cliente_pk").val($(this).data("id"));
}

function editClick(){
	$.ajax({
	  type: "GET",
	  url: "/edit/cliente/",
	  data: { pk: $(this).data("id")},
	  success: function(form){
	  	console.log("Hola!");
	  	$("#editCliente .modal-body").html(form);
	  }
	})
}