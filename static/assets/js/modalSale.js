document.addEventListener("DOMContentLoaded", function () {
    const infoModal = new bootstrap.Modal(document.getElementById("infoModal"));
    const tableModal = new bootstrap.Modal(document.getElementById("tableModal"));
    const tableContainer = document.getElementById("tableContainer");
    const tableModalLabel = document.getElementById("tableModalLabel");

    // Función para obtener el token CSRF
    function getCsrfToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
  
    document.querySelectorAll(".ver-detalles").forEach((elemento) => {
      elemento.addEventListener("click", function () {
        const agenteId = this.getAttribute("data-id");
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
  
        fetch(`/detalle-agente/${agenteId}/`,{
          method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'X-CSRFToken': getCsrfToken()
            },
            body: `start_date=${startDate}&end_date=${endDate}`
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              // Abrir el primer modal
              infoModal.show();
  
              // Configurar botones del primer modal
              document.getElementById("openObamaCare").onclick = function () {
                showTable("ObamaCare", data.data.obama_sales);
              };
  
              document.getElementById("openSupp").onclick = function () {
                showTable("Supp", data.data.supp_sales);
              };
            } else {
              alert("No se pudieron obtener los detalles del agente.");
            }
          })
          .catch((error) => console.error("Error en fetch:", error));
      });
    });
  
    function showTable(type, salesData) {
      // Configurar el título del segundo modal
      tableModalLabel.textContent = `Tabla de ${type}`;
  
      // Limpiar contenedor de la tabla
      tableContainer.innerHTML = "";
  
      // Generar tabla
      if (salesData && salesData.length > 0) {
        const table = document.createElement("table");
        table.classList.add("table", "table-striped", "table-bordered", "table-hover", "table-sm");
  
        // Crear encabezado
        const thead = document.createElement("thead");
        thead.classList.add("table-dark");
        thead.innerHTML = `
          <tr>
            <th>Cliente</th>
            <th>Fecha</th>
            <th>Status</th>
            <th>Company</th>
          </tr>
        `;
        table.appendChild(thead);
  
        // Crear cuerpo de la tabla
        const tbody = document.createElement("tbody");
        salesData.forEach((sale) => {
          const row = `
            <tr>
              <td>${sale.client_name }</td>
              <td>${sale.created_at }</td>
              <td>${sale.details || "No Active" }</td>
              <td>${sale.carrier }</td>
            </tr>
          `;
          tbody.innerHTML += row;
        });
        table.appendChild(tbody);
  
        // Insertar tabla en el contenedor
        tableContainer.appendChild(table);
      } else {
        tableContainer.innerHTML = `<p>No hay datos disponibles para ${type}.</p>`;
      }
  
      // Mostrar el segundo modal y ocultar el primero
      infoModal.hide();
      tableModal.show();
    }
  
    // Botón "Atrás" en el segundo modal
    document.getElementById("backToInfoModal").addEventListener("click", function () {
      // Ocultar el segundo modal y volver al primero
      tableModal.hide();
      infoModal.show();
    });
  });
  