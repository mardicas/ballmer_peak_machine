<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Ballmer Peak Machine</title>
</head>
<body>

<h1>Related <a href="https://xkcd.com/323/" target="blank_">XKCD</a></h1>

<?php
$link = mysqli_connect("mysql", "identity_ro", "ChangeMeToo", "identity") or die("Some error occurred during connection " . mysqli_error($link));

mysqli_set_charset($link,"utf8");

function tablify($sql, $link){
    echo "<table>";
    $query = mysqli_query($link, $sql);
    while($result = mysqli_fetch_array($query))
    {  
        echo "<tr><td>".$result['name']." </td><td> <b>".$result['value']."</b></td></tr>";
    }
    echo "</table>";
}

function dayify($sql, $link){
    echo "<table>";
    $query = mysqli_query($link, $sql);
    while($result = mysqli_fetch_array($query))
    {  
        $dow=date('w', strtotime($result['name']));
        $dowtr=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        echo "<tr><td>".$result['name']." (".$dowtr[$dow].")</td><td> <b>".$result['value']."</b></td></tr>";
    }
    echo "</table>";
}
?>
<table><tr><td valign="top">
<h2>Peak Programmer</h2>
<?php

tablify("SELECT u.name as name, count(o.id) as value FROM orders o, users u WHERE o.rfid=u.rfid GROUP BY o.rfid ORDER BY value DESC", $link);

?>
</td><td width="100px"></td><td valign="top">
<h2>Potential sponsors</h2>
<?php
tablify("SELECT name, credit as value FROM users WHERE credit!=0 ORDER BY credit DESC", $link);
?>
</td></tr><tr><td valign="top">
<h2>Top drinking days</h2>
<?php
dayify("SELECT DATE_FORMAT(aeg, '%Y-%m-%d') as name, count(*) as value FROM orders GROUP BY DATE_FORMAT(aeg, '%Y-%m-%d') ORDER BY value DESC LIMIT 3", $link);
?>

<h2>Top drinking months</h2>
<?php
tablify("SELECT DATE_FORMAT(aeg, '%Y-%m') as name, count(*) as value FROM orders GROUP BY YEAR(aeg), MONTH(aeg) ORDER BY value DESC LIMIT 3", $link);
?>

<h2>Top drinking years</h2>
<?php
tablify("SELECT YEAR(aeg) as name, count(*) as value FROM orders GROUP BY YEAR(aeg) ORDER BY value DESC LIMIT 3", $link);
?>
</td><td width="100px"></td><td valign="top">
<h2>Red or Blue?</h2>
<?php
tablify("SELECT slot as name, count(*) as value FROM orders GROUP BY slot", $link);
?>

<h2>Got lucky!</h2>
<?php
tablify("SELECT rfid as name, count(*) as value FROM orders WHERE rfid='JACKPOT'", $link);
?>
</td></tr></table>

</body>
</html>
<?php
mysqli_close($link);
?>
