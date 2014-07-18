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
});