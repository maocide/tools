<?php
# Author: Mario Negri
# Description:
# Database connection class using pdo

$dbhost = "localhost";
$dbuser = "";
$dbpass = "";
$database_name = ""; 

// strip magic quotes
/*
if (get_magic_quotes_gpc()) {
    function stripslashes_gpc(&$value)
    {
        $value = stripslashes($value);
    }
    array_walk_recursive($_GET, 'stripslashes_gpc');
    array_walk_recursive($_POST, 'stripslashes_gpc');
    array_walk_recursive($_COOKIE, 'stripslashes_gpc');
    array_walk_recursive($_REQUEST, 'stripslashes_gpc');
}
*/


// class autoloader
/*
function __autoload($class) {
    if (class_exists($class, false) || interface_exists($class, false)) {
        return;   
    }
    try {
        if(file_exists('class/Class.' . $class . '.php')) 
          require_once('class/Class.' . $class . '.php');
        else if(file_exists('../class/' . $class . '.php'))
          require_once('class/' . $class . '.php');
        else
          require_once('class/' . $class . '.php');
        if (!(class_exists($class, false) || interface_exists($class, false))) {
            throw new Exception('Class ' . $class . ' not found');
        }
    }
    catch (Exception $e) {
        echo("Autoloader error loading class: $class");
        var_dump($class);
        echo(" Why don't you just do things the right way? Please? Pretty please? ");
    }
}
*/


class connect{

  private function connect_priv(){
    global  $dbhost;
    global  $dbuser;
    global  $dbpass;
    global  $database_name;

    $link = mysql_connect($dbhost, $dbuser, $dbpass);
    if (!$link) {
      die('Could not connect: ' . mysql_error());
    }
    mysql_select_db($database_name)or die("No database!");
  }

  public function connect_db(){
    $this->connect_priv();
  }

}

class DBConnection{
  

  private static $instance;
  private static $dbh;
  private $database_name;
  

  private $charset = "UTF8"; 

  private function __construct(){
    global  $dbhost;
    global  $dbuser;
    global  $dbpass;
    global  $database_name;
    $this->database_name = $database_name;

    self::$dbh = new PDO("mysql:host=$dbhost;dbname=$database_name;", $dbuser, $dbpass);

    #self::$dbh->exec("set names $charset");
    #self::$dbh->exec("SET lc_time_names = 'it_IT';");
    if (!self::$dbh) {
      die('Could not connect');
      print self::$dbh->errorCode();
    }
  }

  public static function getConnection(){
    if(empty(self::$instance)) {
      self::$instance = new DBConnection();
    }
    return self::$instance;
  }
  
  public static function getDbh() {
    return self::$dbh;
  }

  public function getDatabaseName() {
    return $this->database_name;
  }

  function query($query,$param=array()) {
    $dbh = DBConnection::get_connection()->get_dbh();
    $result=array();
    $sql = $query;
    $sth = $dbh->prepare($sql);
    //if ($this->debug) { echo $sql.'</br>';  print_r($param); echo("<br />");};
    $success = $sth->execute($param);
    if(!$success) {
      print("error ");
      print_r($sth->errorInfo());
    }
    $rows = $sth->fetchAll();
    return($rows);
  }

}
?>
