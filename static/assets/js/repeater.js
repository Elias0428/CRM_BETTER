jQuery.fn.extend({
    createRepeater: function (addButtonSelector, containerSelector) {
        var generateId = function (string) {
            return string.replace(/\[/g, '_').replace(/\]/g, '').toLowerCase();
        };

        var repeater = this;
        var template = repeater.find(".items").first().clone();
        var addButton = repeater.find(addButtonSelector);
        var key = repeater.find('.items').length;

        // Limpiar el template para asegurar que los campos estén vacíos
        template.find('input, select').each(function () {
            $(this).val('');
            if ($(this).is('select')) {
                $(this).prop('selectedIndex', 0);
            }
        });

        var addItem = function (key) {
            var itemContent = template.clone();
            var group = itemContent.data("group");
            var inputs = itemContent.find('input, select');

            inputs.each(function () {
                var attrName = $(this).data('name');
                if (attrName) {
                    $(this).attr("name", group + "[" + key + "][" + attrName + "]");
                    $(this).attr('id', generateId(group + "_" + key + "_" + attrName));
                    $(this).parent().find('label').attr('for', generateId(group + "_" + key + "_" + attrName));
                }
            });

            $(containerSelector).append(itemContent); // Añadir al contenedor adecuado
        };

        // Inicializar con los elementos existentes
        repeater.find('.items').each(function (index) {
            var inputs = $(this).find('input, select');
            var group = $(this).data("group");

            inputs.each(function () {
                var attrName = $(this).data('name');
                if (attrName) {
                    $(this).attr("name", group + "[" + index + "][" + attrName + "]");
                    $(this).attr('id', generateId(group + "_" + index + "_" + attrName));
                    $(this).parent().find('label').attr('for', generateId(group + "_" + index + "_" + attrName));
                }
            });
        });

        // Manejar el botón de añadir
        addButton.on("click", function () {
            addItem(key);
            key++;
        });

        // Manejar el botón de eliminar
        repeater.on("click", ".remove-btn", function () {
            $(this).closest('.items').remove();
        });
    }
});

$(document).ready(function () {
    // Llamar a createRepeater para el primer contenedor y botón
    $('#repeater1').createRepeater('.repeater-add-btn-1', '#repeater1');

    // Llamar a createRepeater para el segundo contenedor y botón
    $('#repeater2').createRepeater('.repeater-add-btn-2', '#repeater2');
});
