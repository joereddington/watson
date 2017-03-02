<?php
//All code from http://www.w3schools.com/php/php_file_upload.asp with thanks
#echo var_dump($_REQUEST);
$command = 'python process.py '.str_replace("\n","hope",$_POST["content"]);
$temp = shell_exec($command );
#echo $_POST["content"];
echo "Here";
echo nl2br($temp);
?>

