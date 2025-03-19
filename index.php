<?php
// Database connection parameters
$host = "dbs.spskladno.cz";
$user = "student6";
$password = "spsnet";
$dbname = "vyuka6";

// Create connection
$conn = new mysqli($host, $user, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to fetch top 10 scores for a given difficulty
function getTopScores($difficulty) {
    global $conn;
    $sql = "SELECT h.jmeno, s.skore
            FROM 1skore s
            JOIN 1hraci h ON s.player_id = h.id
            JOIN 1obtiznosti o ON s.difficulty_id = o.id
            WHERE o.difficulty_name = ?
            ORDER BY s.skore DESC
            LIMIT 10";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $difficulty);
    $stmt->execute();
    $result = $stmt->get_result();
    $scores = [];
    while ($row = $result->fetch_assoc()) {
        $scores[] = $row;
    }
    return $scores;
}

// Fetch scores for each difficulty
$easyScores = getTopScores("easy");
$mediumScores = getTopScores("medium");
$hardScores = getTopScores("hard");

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top 10 Scores</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 80%;
            margin: 50px auto;
        }
        table {
            width: 100%;
            margin-bottom: 30px;
            border-collapse: collapse;
        }
        table th, table td {
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        table th {
            background-color: #4CAF50;
            color: white;
        }
        h1 {
            text-align: center;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Top 10 pro každou obtížnost</h1>

    <!-- Easy Difficulty Table -->
    <h2>Lehká</h2>
    <table>
        <tr>
            <th>Pořadí</th>
            <th>Jméno</th>
            <th>Skóre</th>
        </tr>
        <?php foreach ($easyScores as $index => $score): ?>
            <tr>
                <td><?php echo $index + 1; ?></td>
                <td><?php echo htmlspecialchars($score['jmeno']); ?></td>
                <td><?php echo $score['skore']; ?></td>
            </tr>
        <?php endforeach; ?>
    </table>

    <!-- Medium Difficulty Table -->
    <h2>Střední</h2>
    <table>
        <tr>
            <th>Pořadí</th>
            <th>Jméno</th>
            <th>Skóre</th>
        </tr>
        <?php foreach ($mediumScores as $index => $score): ?>
            <tr>
                <td><?php echo $index + 1; ?></td>
                <td><?php echo htmlspecialchars($score['jmeno']); ?></td>
                <td><?php echo $score['skore']; ?></td>
            </tr>
        <?php endforeach; ?>
    </table>

    <!-- Hard Difficulty Table -->
    <h2>Těžká</h2>
    <table>
        <tr>
            <th>Pořadí</th>
            <th>Jméno</th>
            <th>Skóre</th>
        </tr>
        <?php foreach ($hardScores as $index => $score): ?>
            <tr>
                <td><?php echo $index + 1; ?></td>
                <td><?php echo htmlspecialchars($score['jmeno']); ?></td>
                <td><?php echo $score['skore']; ?></td>
            </tr>
        <?php endforeach; ?>
    </table>
</div>

</body>
</html>

<?php
// Close the database connection
$conn->close();
?>
