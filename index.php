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

// Start the session
session_start();

// Function to fetch top 10 scores for a given difficulty
function getTopScores($difficulty) {
    global $conn;
    $sql = "SELECT s.player_id, s.difficulty_id, s.skore, h.jmeno
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
        $scores[] = $row;  // Include player_id and difficulty_id in the result set
    }
    return $scores;
}

// Fetch scores for each difficulty
$easyScores = getTopScores("easy");
$mediumScores = getTopScores("medium");
$hardScores = getTopScores("hard");

// Function to get all registered users (for admin view)
function getUsers() {
    global $conn;
    $sql = "SELECT id, jmeno FROM 1hraci";  
    $result = $conn->query($sql);
    $users = [];
    while ($row = $result->fetch_assoc()) {
        $users[] = $row;
    }
    return $users;
}

// Function to get all scores for a specific user
function getUserScores($userId) {
    global $conn;
    $sql = "SELECT s.skore, o.difficulty_name
            FROM 1skore s
            JOIN 1obtiznosti o ON s.difficulty_id = o.id
            WHERE s.player_id = ? 
            ORDER BY o.difficulty_name";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $userId);
    $stmt->execute();
    $result = $stmt->get_result();
    $userScores = [];
    while ($row = $result->fetch_assoc()) {
        $userScores[] = $row;
    }
    return $userScores;
}




// Admin delete score functionality
if (isset($_POST['delete_score']) && isset($_POST['player_id']) && isset($_POST['difficulty_id']) && isset($_POST['skore'])) {
    if ($_SESSION['is_admin'] == true) {
        // Získání hodnot z formuláře
        $player_id = $_POST['player_id'];
        $difficulty_id = $_POST['difficulty_id'];
        $skore = $_POST['skore'];

        // SQL dotaz pro odstranění skóre
        $sql = "DELETE FROM 1skore WHERE player_id = ? AND difficulty_id = ?";
        $stmt = $conn->prepare($sql);
        if ($stmt === false) {
            die('Error in preparing the SQL query: ' . $conn->error);
        }

        // Bind the parameters and execute the statement
        $stmt->bind_param("ii", $player_id, $difficulty_id);  // "ii" - integer, integer
        $stmt->execute();

       
    }
       
}


// Handle user login/logout
if (isset($_POST['login'])) {
    // Získání uživatelského jména a hesla z formuláře
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Předpokládáme, že hesla jsou v databázi uložena zašifrovaná
    $hashed_password = hash('sha256', $password); // Šifrování hesla pomocí SHA-256

    // SQL dotaz pro získání uživatele podle jména a hesla
    $sql = "SELECT * FROM 1hraci WHERE jmeno = ? AND heslo = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ss", $username, $hashed_password); 
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        // Pokud je uživatel nalezen, přihlásíme ho
        $user = $result->fetch_assoc();
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['jmeno'];
        $_SESSION['is_admin'] = $user['is_admin']; 

        // Redirect nebo zobrazení úspěšné zprávy
        header('Location: index.php'); 
        exit();
    } else {
        echo "<p style='color:red;'>Chyba: Nesprávné jméno nebo heslo</p>";
    }
}

if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: index.php');
    exit();
}

// Handle user registration
if (isset($_POST['register'])) {
    // Získání uživatelského jména a hesla z formuláře
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Předpokládáme, že hesla jsou v databázi uložena zašifrovaná
    $hashed_password = hash('sha256', $password); 

    // Zkontroluj, jestli uživatel s tímto jménem již existuje
    $sql = "SELECT * FROM 1hraci WHERE jmeno = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        echo "<p style='color:red;'>Tento uživatel již existuje.</p>";
    } else {
        // Vložení nového uživatele do databáze
        $sql = "INSERT INTO 1hraci (jmeno, heslo) VALUES (?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ss", $username, $hashed_password);
        $stmt->execute();
        
        echo "<p style='color:green;'>Registrace byla úspěšná! Můžete se přihlásit.</p>";
    }
}
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
        /* Modal (vyskakovací okno) */
        .modal {
            display: none; 
            position: fixed; 
            z-index: 1; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%;
            background-color: rgba(0,0,0,0.4); 
            padding-top: 60px;
        }
        .modal-content {
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }
        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
<?php
    // Kontrola, zda existuje $_SESSION['is_admin'], pokud ne, nastavíme výchozí hodnotu false
    $is_admin = isset($_SESSION['is_admin']) ? $_SESSION['is_admin'] : false;
?>
<div class="container">
    <h1>Top 10 pro každou obtížnost</h1>

    <!-- Login/Logout Form -->
    <div style="text-align: right;">
        <?php if (!isset($_SESSION['username'])): ?>
            <a href="#" onclick="document.getElementById('loginModal').style.display='block'">Login</a> |
            <a href="#" onclick="document.getElementById('registerModal').style.display='block'">Register</a>
        <?php else: ?>
            <p>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>! <a href="?logout=true">Logout</a></p>
        <?php endif; ?>
    </div>

    <!-- Modal Login -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="document.getElementById('loginModal').style.display='none'">&times;</span>
            <h2>Login</h2>
            <form method="POST">
                <label for="username">Jméno:</label><br>
                <input type="text" id="username" name="username" required><br><br>
                <label for="password">Heslo:</label><br>
                <input type="password" id="password" name="password" required><br><br>
                <input type="submit" name="login" value="Přihlásit se">
            </form>
        </div>
    </div>

    <!-- Modal Register -->
    <div id="registerModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="document.getElementById('registerModal').style.display='none'">&times;</span>
            <h2>Registrace</h2>
            <form method="POST">
                <label for="username">Jméno:</label><br>
                <input type="text" id="username" name="username" required><br><br>
                <label for="password">Heslo:</label><br>
                <input type="password" id="password" name="password" required><br><br>
                <input type="submit" name="register" value="Zaregistrovat se">
            </form>
        </div>
    </div>

    <!-- Displaying Scores -->
    <!-- Show User Scores -->
    <?php if (isset($_SESSION['user_id'])): ?>
        <h2>Vaše skóre</h2>
        <table>
            <tr>
                <th>Obtížnost</th>
                <th>Skóre</th>
            </tr>
            <?php
                $userScores = getUserScores($_SESSION['user_id']);
                foreach ($userScores as $score):
            ?>
                <tr>
                    <td><?php echo htmlspecialchars($score['difficulty_name']); ?></td>
                    <td><?php echo $score['skore']; ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
    <?php endif; ?>

    <!-- Displaying Top Scores -->
    <!-- Easy Difficulty Table -->
    <h2>Lehká</h2>
    <table>
        <tr>
            <th>Pořadí</th>
            <th>Jméno</th>
            <th>Skóre</th>
            <?php if ($is_admin == true): ?>
                <th>Akce</th>
            <?php endif; ?>
        </tr>
        <?php foreach ($easyScores as $index => $score): ?>
            <tr>
                <td><?php echo $index + 1; ?></td>
                <td><?php echo htmlspecialchars($score['jmeno']); ?></td>
                <td><?php echo $score['skore']; ?></td>
                <?php if ($is_admin == true): ?>
                    <td>
                        <form method="POST" action="">
                            <input type="hidden" name="player_id" value="<?php echo $score['player_id']; ?>">
                            <input type="hidden" name="difficulty_id" value="<?php echo $score['difficulty_id']; ?>">
                            <input type="hidden" name="skore" value="<?php echo $score['skore']; ?>">
                            <button type="submit" name="delete_score">Smazat</button>
                        </form>

                    </td>   
                <?php endif; ?>
            </tr>
        <?php endforeach; ?>
    </table>


    <h2>Střední</h2>
    <table>
        <tr>
            <th>Pořadí</th>
            <th>Jméno</th>
            <th>Skóre</th>
            <?php if ($is_admin == true): ?>
                <th>Akce</th>
            <?php endif; ?>
        </tr>
        <?php foreach ($mediumScores as $index => $score): ?>
            <tr>
                <td><?php echo $index + 1; ?></td>
                <td><?php echo htmlspecialchars($score['jmeno']); ?></td>
                <td><?php echo $score['skore']; ?></td>
                <?php if ($is_admin == true): ?>
                    <td>
                        <form method="POST" action="">
                            <input type="hidden" name="player_id" value="<?php echo $score['player_id']; ?>">
                            <input type="hidden" name="difficulty_id" value="<?php echo $score['difficulty_id']; ?>">
                            <input type="hidden" name="skore" value="<?php echo $score['skore']; ?>">
                            <button type="submit" name="delete_score">Smazat</button>
                        </form>
                    </td>
                <?php endif; ?>
            </tr>
        <?php endforeach; ?>
    </table>


    <h2>Težká</h2>
    <table>
        <tr>
            <th>Pořadí</th>
            <th>Jméno</th>
            <th>Skóre</th>
            <?php if ($is_admin == true): ?>
                <th>Akce</th>
            <?php endif; ?>
        </tr>
        <?php foreach ($hardScores as $index => $score): ?>
            <tr>
                <td><?php echo $index + 1; ?></td>
                <td><?php echo htmlspecialchars($score['jmeno']); ?></td>
                <td><?php echo $score['skore']; ?></td>
                <?php if ($is_admin == true): ?>
                    <td>
                        <form method="POST" action="">
                            <input type="hidden" name="player_id" value="<?php echo $score['player_id']; ?>">
                            <input type="hidden" name="difficulty_id" value="<?php echo $score['difficulty_id']; ?>">
                            <input type="hidden" name="skore" value="<?php echo $score['skore']; ?>">
                            <button type="submit" name="delete_score">Smazat</button>
                        </form>
                    </td>
                <?php endif; ?>
            </tr>
        <?php endforeach; ?>
    </table>

</div>

<script>
    // Umožní uzavření modálních oken
    window.onclick = function(event) {
        if (event.target == document.getElementById('loginModal') || event.target == document.getElementById('registerModal')) {
            document.getElementById('loginModal').style.display = "none";
            document.getElementById('registerModal').style.display = "none";
        }
    }
</script>

</body>
</html>
