document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('buttonSendObama')?.addEventListener('click', saveAcaPlan);
    document.getElementById('buttonSendSupp')?.addEventListener('click', saveSupplementaryPlan);
    document.getElementById('buttonSendDepend')?.addEventListener('click', saveDependents);

    const addButton = document.getElementById('initDatePickerBtn');

    if (addButton) {
      addButton.addEventListener('click', () => {
        // Aquí podrías tener lógica para agregar un nuevo dependiente
        // Simula el proceso de agregar un dependiente dinámicamente
        if (idAcaPlan === "ACA") { addTypesDependentACA(); } else{ addTypesDependent(); }
        
        
        // Llama a addTypesDependent después de que el DOM se haya actualizado
        setTimeout(() => {
          if (idAcaPlan === "ACA") { addTypesDependentACA();} else{ addTypesDependent(); }
        }, 0); // Asegura que se ejecute después de la actualización del DOM
      });
    } 
});

var idAcaPlan
var id_aca_plan

function saveAcaPlan() {

    var formData = new FormData();
    formData.append('type_sales', type_sales)
    formData.append('taxes', document.getElementById('taxes').value)
    formData.append('agent_usa', document.getElementById('agent_usa').value)
    formData.append('planName', document.getElementById('planName').value)
    formData.append('work', document.getElementById('work').value)
    formData.append('subsidy', document.getElementById('subsidy').value)
    formData.append('carrierObama', document.getElementById('carrierObama').value)
    formData.append('observationObama', document.getElementById('observationObama').value)
    formData.append('doc_income', document.getElementById('doc_income').value)
    formData.append('doc_migration', document.getElementById('doc_migration').value)
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value)
    formData.append('premium', document.getElementById('premium').value) 

    var acaPlanId = document.getElementById('acaPlanId').value;
    var acaPlan = document.getElementById('acaPlan').value;
    if (acaPlanId) {
      formData.append('acaPlanId', acaPlanId);
    }

  
    fetch(`/fetchAca/${client_id}/`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Actualizar la interfaz de usuario según sea necesario
        id_aca_plan = data.aca_plan_id
        stepper1.next();
        idAcaPlan = acaPlan
        if (idAcaPlan == 'ACA') {
          //console.log(idAcaPlan);
          addTypesDependentACA();
        }       
        
      } else {
        // Manejar errores
      }
    })
    .catch(error => {
      // Manejar errores
    });
}
  
function saveSupplementaryPlan() {
  var formData = new FormData();
  formData.append('type_sales', type_sales);
  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

  // Recorrer todos los conjuntos de dependientes
  const plans = document.querySelectorAll('.supplementaryClassList'); // Ajustado el selector aquí
  plans.forEach((plan, index) => {
    // Obtener los valores de cada conjunto de dependientes
      
      
      const carrierSuple = plan.querySelector('[name="carrierSuple"]').value;
      const agent_usa = plan.querySelector('[name="agent_usa"]').value;
      const premiumSupp = plan.querySelector('[name="premiumSupp"]').value;
      const policyTypeSupp = plan.querySelector('[name="policyTypeSupp"]').value;
      const preventiveSupp = plan.querySelector('[name="preventiveSupp"]').value;
      const coverageSupp = plan.querySelector('[name="coverageSupp"]').value;
      const deducibleSupp = plan.querySelector('[name="deducibleSupp"]').value;
      const observationSuple = plan.querySelector('[name="observationSuple"]').value;
      const suppIdField = plan.querySelector('[name="suppId"]'); 

      
      let suppId = suppIdField ? suppIdField.value : '';

      if (!validarYActualizarFechaSupp()){
        return;
      }

      //fecha estilo USA
      const effectiveDateSupp = plan.querySelector('[name="effectiveDateSupp"]').value;
      // Separar la fecha en partes: mes, día, y año
      const [month, day, year] = effectiveDateSupp.split('-');
      // Reorganizar la fecha a formato año/mes/día
      const effectiveDateSuppFormatted = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;



      // Validar si hay un nombre ingresado, para evitar enviar campos vacíos
      if (agent_usa.trim() !== '') {
          // Agregar cada dependiente al formData con un índice
          if (plan.querySelector('[name="suppId"]')){
            formData.append(`supplementary_plan_data[${index}][id]`, suppId);
          }          
          formData.append(`supplementary_plan_data[${index}][effectiveDateSupp]`, effectiveDateSuppFormatted);
          formData.append(`supplementary_plan_data[${index}][agent_usa]`, agent_usa);
          formData.append(`supplementary_plan_data[${index}][carrierSuple]`, carrierSuple);
          formData.append(`supplementary_plan_data[${index}][premiumSupp]`, premiumSupp);
          formData.append(`supplementary_plan_data[${index}][policyTypeSupp]`, policyTypeSupp);
          formData.append(`supplementary_plan_data[${index}][preventiveSupp]`, preventiveSupp);
          formData.append(`supplementary_plan_data[${index}][coverageSupp]`, coverageSupp);
          formData.append(`supplementary_plan_data[${index}][deducibleSupp]`, deducibleSupp);
          formData.append(`supplementary_plan_data[${index}][observationSuple]`, observationSuple);
      }
  });

  // Realizar la solicitud fetch
  fetch(`/fetchSupp/${client_id}/`, {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          //console.log('IDs actualizados:', data.supp_ids);
          plans.forEach((plan, index) => {
            suppIdInputHidden = plan.querySelector('[name="suppId"]')
            //console.log(suppIdInputHidden)
            if (suppIdInputHidden.value == ''){
              // si imput esta vacio se le coloca el id recivido del parte del bakend
              suppIdInputHidden.value = data.supp_ids[index]
            }
          });

          // Actualizar la interfaz de usuario según sea necesario
          stepper1.next();
          addTypesDependent()
      } else {
          // Manejar errores
          //console.error('Error en la respuesta:', data);
      }
  })
  .catch(error => {
    //console.error('Error en la solicitud:', error);
  });
}
  
function saveDependents() {
  var formData = new FormData();
  formData.append('type_sales', 'DEPENDENTS');
  formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

  //console.log('Formulario inicializado con CSRF:', document.querySelector('[name=csrfmiddlewaretoken]').value);  // Verificar CSRF

  // Recorrer todos los conjuntos de dependientes
  const dependents = document.querySelectorAll('.dependentClassList'); // Ajustado el selector aquí.
  dependents.forEach((dependent, index) => {
    //console.log(`Procesando dependiente ${index + 1}...`); // Verificar el índice del dependiente procesado

    // Obtener los valores de cada conjunto de dependientes
    const kinship = dependent.querySelector('[name="kinship"]').value;
    const nameDependent = dependent.querySelector('[name="nameDependent"]').value;
    const applyDependent = dependent.querySelector('[name="applyDependent"]').value;    
    const migrationStatusDependent = dependent.querySelector('[name="migrationStatusDependent"]').value;
    const sexDependent = dependent.querySelector('[name="sexDependent"]').value;

    // Validar si el nombre del dependiente está vacío o si algún campo necesario falta
    if (nameDependent.trim() === '' || kinship.trim() === '' || applyDependent.trim() === '' || migrationStatusDependent.trim() === '' || sexDependent.trim() === '') {
      if (submitButton) {
        submitButton.disabled = true;
      }
    
      return; // Si algún campo obligatorio está vacío, se omite este dependiente.
    }

    if (!validarYActualizarFecha()){
      return;
    }

    //fecha estilo USA
    const dateBirthDependent = dependent.querySelector('[name="dateBirthDependent"]').value;
    // Separar la fecha en partes: mes, día, y año
    const [month, day, year] = dateBirthDependent.split('-');
    // Reorganizar la fecha a formato año/mes/día
    const dateBirthDependentFormatted = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;


    // Ajuste aquí para obtener los valores seleccionados de un select múltiple
    const typePoliceField = dependent.querySelector('[name="typePoliceDependents[]"]');
    let typePolice = [];

    // Si el campo select existe, obtener los valores seleccionados
    if (typePoliceField) {
        // Obtener los valores seleccionados
        typePolice = Array.from(typePoliceField.selectedOptions)
            .map(option => option.value);
        
        // Mostrar los valores seleccionados en 'typePolice'
        //console.log('Valores seleccionados en typePolice:', typePolice);
    }
    
    if(typePoliceField.value.trim() === ''){
      if (submitButton) {
        submitButton.disabled = true;
      }
      return
    }
    // Aquí estamos manejando el 'dependentId' como lo hicimos antes
    const dependentIdField = dependent.querySelector('[name="dependentId"]');
    let dependentId = dependentIdField ? dependentIdField.value : '';

    // Mostrar el dependentId
    //console.log('Dependent ID:', dependentId);

    // Validar si hay un nombre ingresado, para evitar enviar campos vacíos
    if (nameDependent.trim() !== '') {
        //console.log('Enviando dependiente al formData:', index + 1);

        // Agregar cada dependiente al formData con un índice
        if (dependentId) {
          formData.append(`dependent[${index}][id]`, dependentId);
        }
        formData.append(`dependent[${index}][kinship]`, kinship);
        formData.append(`dependent[${index}][nameDependent]`, nameDependent);
        formData.append(`dependent[${index}][applyDependent]`, applyDependent);
        formData.append(`dependent[${index}][dateBirthDependent]`, dateBirthDependentFormatted);
        formData.append(`dependent[${index}][migrationStatusDependent]`, migrationStatusDependent);
        formData.append(`dependent[${index}][sexDependent]`, sexDependent);
        
        // Si se han seleccionado opciones en 'typePolice', agregarlas
        if (typePolice.length > 0) {
          formData.append(`dependent[${index}][typePoliceDependents]`, typePolice);
          //console.log('Agregando typePolice al formData:', typePolice);  // Verificar qué valores de 'typePolice' se agregan
        }
    }
    
  });

  //console.log('FormData antes de la solicitud fetch:', formData);

  // Realizar la solicitud fetch
  fetch(`/fetchDependent/${client_id}/`, {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      //console.log('Respuesta del servidor:', data);  // Verificar la respuesta del servidor

      if (data.success) {
          //console.log('IDs actualizados:', data.dependents_ids);
          //console.log('Éxito:', data.success);
          
          // Actualizar la interfaz de usuario según sea necesario
          stepper1.next();
          if (data.success) {

          // Mostrar el modal con Bootstrap
          const successModal = new bootstrap.Modal(document.getElementById('successModal'));
          successModal.show();

          // Botón 1: Redirigir a la página de inicio
          document.getElementById('buttonHome').addEventListener('click', () => {
            window.location.href = '/';
          });

          // Botón 2: Redirigir a los detalles
          document.getElementById('buttonConsentEng').addEventListener('click', () => {    
            window.open(`/viewConsent/${id_aca_plan}/?lenguaje=en`, '_blank');
          });
          document.getElementById('buttonConsentSpa').addEventListener('click', () => {    
            window.open(`/viewConsent/${id_aca_plan}/?lenguaje=es`, '_blank');
          });


          }
      } else {
          // Manejar errores
          //console.error('Error en la respuesta:', data);
      }
  })
  .catch(error => {
      //console.error('Error en la solicitud:', error);
  });
}

function addTypesDependent() {
  const policyTypeSuppSelects = document.querySelectorAll('select[name="policyTypeSupp"]');
  const typePoliceSelects = document.querySelectorAll('select[name="typePoliceDependents[]"]');
  
  // Verificar que se encuentren los selects necesarios
  if (policyTypeSuppSelects.length === 0 || typePoliceSelects.length === 0) {
    return;
  }
  
  
  // Agregar opciones dinámicamente dependiendo del select policyTypeSupp
  policyTypeSuppSelects.forEach(policySelect => {
    const selectedPolicyType = policySelect.value; // Obtener el valor seleccionado de policyTypeSupp
  
    if (selectedPolicyType) {
      typePoliceSelects.forEach(typePoliceSelect => {
        // Verificar si la opción ya existe en el select
        const optionExists = Array.from(typePoliceSelect.options).some(option => option.value === selectedPolicyType);
        if (!optionExists) {
          const newOption = document.createElement('option');
          newOption.value = selectedPolicyType;
          newOption.textContent = selectedPolicyType;
          typePoliceSelect.appendChild(newOption); // Añadir la opción al select
        }
      });
    }
  });
  
  // Verificar si idAcaPlan es "ACA" y agregar la opción "ACA" si es necesario
  console.log(idAcaPlan);
  if (idAcaPlan === "ACA" || idAcaPlan === "ACA/SUPLEMENTARIO") {
    typePoliceSelects.forEach(typePoliceSelect => {
      // Verificar si la opción 'ACA' ya existe
      const optionExists = Array.from(typePoliceSelect.options).some(option => option.value === "ACA");
      if (!optionExists) {
        const newOption = document.createElement('option');
        newOption.value = "ACA";  // Establecer el valor de la opción
        newOption.textContent = "ACA";  // Establecer el texto visible de la opción
        typePoliceSelect.appendChild(newOption); // Añadir la opción "ACA" al select
      }
    });
  }
  
  // Inicializar Choices.js solo si no tiene la clase 'choices__input'
  typePoliceSelects.forEach(select => {
    if (!select.classList.contains('choices__input')) {
      new Choices(select, {
        removeItemButton: true,
        searchEnabled: true,
        placeholder: true,
        placeholderValue: 'Select options',
      });
    }
  });
}

function addTypesDependentACA() {
  
  const typePoliceSelects = document.querySelectorAll('select[name="typePoliceDependents[]"]');

  // Verificar si idAcaPlan es "ACA" y agregar la opción "ACA" si es necesario
  console.log(idAcaPlan)
  if (idAcaPlan === "ACA") {
    typePoliceSelects.forEach(typePoliceSelect => {
      // Verificar si la opción 'ACA' ya existe
      const optionExists = Array.from(typePoliceSelect.options).some(option => option.value === "ACA");
      if (!optionExists) {
        const newOption = document.createElement('option');
        newOption.value = "ACA";  // Establecer el valor de la opción
        newOption.textContent = "ACA";  // Establecer el texto visible de la opción
        typePoliceSelect.appendChild(newOption); // Añadir la opción "ACA" al select
      }
    });
  }

  // Inicializar Choices.js solo si no tiene la clase 'choices__input'
  typePoliceSelects.forEach(select => {
    if (!select.classList.contains('choices__input')) {
      new Choices(select, {
        removeItemButton: true,
        searchEnabled: true,
        placeholder: true,
        placeholderValue: 'Select options',
      });
    }
  });
}

function validarYActualizarFecha() {
  var inputsDate = document.querySelectorAll('#dateBirthDependent');

  const isValid = true
  inputsDate.forEach(inputFecha => {
    // Validar que la fecha tenga el formato MM-DD-AAAA
    const fechaRegex = /^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-\d{4}$/;
    if (!fechaRegex.test(inputFecha.value)) {
      inputFecha.focus();
      alert('La fecha no tiene el formato válido MM-DD-AAAA');
      isValid = false;
    }

    // Separar la fecha en mes, día y año
    const [mes, dia, año] = inputFecha.value.split('-').map(num => parseInt(num));

    // Validar si el año es bisiesto
    const esBisiesto = (año % 4 === 0 && (año % 100 !== 0 || año % 400 === 0));

    // Validar la cantidad de días en el mes
    const diasPorMes = {
      1: 31, 2: esBisiesto ? 29 : 28, 3: 31, 4: 30,
      5: 31, 6: 30, 7: 31, 8: 31, 9: 30,
      10: 31, 11: 30, 12: 31
    };

    // Validar que el día sea válido para ese mes
    if (dia < 1 || dia > diasPorMes[mes]) {
      alert('El día no es válido para el mes indicado');
      isValid = false;
    }
  });
  return isValid;
}

function validarYActualizarFechaSupp() {
  var inputsDate = document.querySelectorAll('#effectiveDateSupp');

  const isValid = true
  inputsDate.forEach(inputFecha => {
    // Validar que la fecha tenga el formato MM-DD-AAAA
    const fechaRegex = /^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-\d{4}$/;
    if (!fechaRegex.test(inputFecha.value)) {
      inputFecha.focus();
      alert('La fecha no tiene el formato válido MM-DD-AAAA');
      isValid = false;
    }

    // Separar la fecha en mes, día y año
    const [mes, dia, año] = inputFecha.value.split('-').map(num => parseInt(num));

    // Validar si el año es bisiesto
    const esBisiesto = (año % 4 === 0 && (año % 100 !== 0 || año % 400 === 0));

    // Validar la cantidad de días en el mes
    const diasPorMes = {
      1: 31, 2: esBisiesto ? 29 : 28, 3: 31, 4: 30,
      5: 31, 6: 30, 7: 31, 8: 31, 9: 30,
      10: 31, 11: 30, 12: 31
    };

    // Validar que el día sea válido para ese mes
    if (dia < 1 || dia > diasPorMes[mes]) {
      alert('El día no es válido para el mes indicado');
      isValid = false;
    }
  });
  return isValid;
}