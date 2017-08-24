# seek_thermal_01
Software en Python que permite controlar la cámara SeekThermal,además es posible adquirir imágenes y almacenarlas en formato  .TIFF. Por otra parte el software incluye un algoritmo que elimina el ruido de patrón Hexagonal, por lo tanto las imágenes almacenadas correspponden al RawData 16 bit sin ningún tipo de compresión ni procesado de imagen.

Requisitos: 

1. Este software esta diseñado para sistemas operativos Linux.
2. PC o Raspberry Pi 2/3
3. Python 2.7

Instrucciones:

1. Instalar módulos conforme al archivo requeriments.txt
    $ pip install -r requirements.txt
2. Instalar módulo PyQt 
    $ pip install PyQt4 

Uso:
En la carpeta seek_thermal_01 ejecute el terminal y escriba el siguiente comando:

   $ sudo python seek_gui_01.py o $sudo python seek_gui_02.py
   



