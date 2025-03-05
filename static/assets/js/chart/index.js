document.addEventListener("DOMContentLoaded", function() {
    // Obtener el elemento script con los datos del gráfico
    const chartDataElement = document.getElementById('chartData');

    // Verificar si el elemento con los datos existe
    if (!chartDataElement) {
        //console.error("No se encontró el script con los datos del gráfico.");
        return;
    }

    // Obtener los datos JSON y convertirlos a un objeto
    const chartData = JSON.parse(chartDataElement.textContent);

    // Verificar si los datos se han cargado correctamente
    //console.log("chartData:", chartData);

    // Extraer los datos para el gráfico
    const usernames = chartData.map(item => item.username);
    const obamacareCounts = chartData.map(item => item.obamacare_count);
    const obamacareTotalCounts = chartData.map(item => item.obamacare_count_total);
    const suppCounts = chartData.map(item => item.supp_count);
    const suppTotalCounts = chartData.map(item => item.supp_count_total);

    // Configuración de ApexCharts
    var options = {
        series: [{
            name: 'ObamaCare Active',
            data: obamacareCounts
        }, {
            name: 'ObamaCare Total',
            data: obamacareTotalCounts
        }, {
            name: 'Supp Active',
            data: suppCounts
        }, {
            name: 'Supp Total',
            data: suppTotalCounts
        }],
        chart: {
            foreColor: '#9ba7b2',
            type: 'bar',
            height: 360
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                endingShape: 'rounded'
            },
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
        },
        title: {
            text: 'Sales Agent Data',
            align: 'left',
            style: {
                fontSize: '14px'
            }
        },
        colors: ["#0d6efd", '#f01118', '#28a745', '#ffc107'],
        xaxis: {
            categories: usernames,  // Nombres de usuario como categorías
        },
        yaxis: {
            title: {
                text: 'Count'
            }
        },
        fill: {
            opacity: 1
        },
        tooltip: {
            theme: 'dark',  // Esto asegura que el tooltip tenga un fondo oscuro
            y: {
                formatter: function(val) {
                    return val + " items";
                }
            }
        }
    };

    // Verifica si tienes el contenedor adecuado en el HTML
    const chartContainer = document.querySelector("#chartIndex");
    if (chartContainer) {
        // Crear el gráfico ApexCharts
        var chart = new ApexCharts(chartContainer, options);
        chart.render();
    } else {
        //console.error("El contenedor del gráfico con id 'chartIndex' no existe.");
    }
});
