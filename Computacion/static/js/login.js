$('.form').find('input, textarea').on('keyup blur focus', function (e) {
  
    var $this = $(this),
        label = $this.prev('label');
  
        if (e.type === 'keyup') {
              if ($this.val() === '') {
            label.removeClass('active highlight');
          } else {
            label.addClass('active highlight');
          }
      } else if (e.type === 'blur') {
          if( $this.val() === '' ) {
              label.removeClass('active highlight'); 
              } else {
              label.removeClass('highlight');   
              }   
      } else if (e.type === 'focus') {
        
        if( $this.val() === '' ) {
              label.removeClass('highlight'); 
              } 
        else if( $this.val() !== '' ) {
              label.addClass('highlight');
              }
      }
  
  });
  
  $('.tab a').on('click', function (e) {
    
    e.preventDefault();
    
    $(this).parent().addClass('active');
    $(this).parent().siblings().removeClass('active');
    
    target = $(this).attr('href');
  
    $('.tab-content > div').not(target).hide();
    
    $(target).fadeIn(600);
    
  });

  // Función para desvanecer los mensajes de éxito después de un tiempo determinado
// Función para desvanecer los mensajes de error
function fadeOutErrorMessages() {
  // Seleccionar todos los elementos con la clase "error-message"
  const errorMessages = document.querySelectorAll('.error-message');

  // Establecer el tiempo (en milisegundos) durante el cual se mostrarán los mensajes de error
  const fadeOutTime = 5000; // 5000 ms = 5 segundos

  // Recorrer cada mensaje de error y aplicar la animación para desvanecer
  errorMessages.forEach((message) => {
      // Desvanecer gradualmente el mensaje durante el tiempo especificado
      $(message).fadeOut(fadeOutTime, function() {
          // Eliminar el mensaje del DOM después de que se haya desvanecido
          $(this).remove();
      });
  });
}

// Llamar a la función para desvanecer los mensajes de error al cargar la página
$(document).ready(function() {
  fadeOutErrorMessages();
});