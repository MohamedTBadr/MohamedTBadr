<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mohamed Badr — Backend Developer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: #f9faff;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        header {
            text-align: center;
            padding-bottom: 40px;
        }

        header h1 {
            font-size: 2.5rem;
            color: #007ACC;
        }

        header h2 {
            font-size: 1.5rem;
            color: #555;
            margin-top: 10px;
        }

        section {
            margin-bottom: 40px;
        }

        h3 {
            color: #007ACC;
            margin-bottom: 10px;
        }

        .muted {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }

        .badges img {
            margin: 4px;
            vertical-align: middle;
        }

        a {
            color: #007ACC;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .project {
            margin-bottom: 20px;
        }

        hr {
            border: 0;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }

        blockquote {
            font-style: italic;
            color: #555;
            border-left: 4px solid #007ACC;
            padding-left: 15px;
            margin: 20px 0;
        }
    </style>
</head>

<body>

    <div class="container">
        <header>
            <h1>Hi there 👋, I'm Mohamed Badr</h1>
            <h2>Backend Developer | Full-Stack Enthusiast</h2>
        </header>

        <section>
            <h3>🚀 About Me</h3>
            <p>Full-Stack Developer building modern web applications with <strong>Laravel, Angular, and ASP.NET Core</strong>.<br>
            Passionate about <strong>real-time systems, backend architecture, and clean, maintainable code</strong>.<br>
            I enjoy automating workflows and creating practical solutions for real-world problems.</p>
            <ul class="muted">
                <li>🌱 Currently learning: <strong>Advanced Laravel, SignalR, WebSockets, ASP.NET Core</strong></li>
                <li>💼 Open to opportunities in <strong>Backend & Full-Stack Development</strong></li>
                <li>⚡ Fun fact: I love turning ideas into real-world applications</li>
            </ul>
        </section>

        <hr>

        <section>
            <h3>🛠 Skills</h3>

            <h4>Frontend</h4>
            <div class="badges" align="left">
                <img src="https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML">
                <img src="https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS">
                <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JS">
                <img src="https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white" alt="Angular">
                <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap">
            </div>

            <h4>Backend</h4>
            <div class="badges" align="left">
                <img src="https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white" alt="PHP">
                <img src="https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white" alt="Laravel">
                <img src="https://img.shields.io/badge/ASP.NET-512BD4?style=for-the-badge&logo=dotnet&logoColor=white" alt="ASP.NET">
                <img src="https://img.shields.io/badge/REST API-blue?style=for-the-badge" alt="REST API">
                <img src="https://img.shields.io/badge/SignalR-6D2B9E?style=for-the-badge" alt="SignalR">
            </div>

            <h4>Database</h4>
            <div class="badges" align="left">
                <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
                <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
                <img src="https://img.shields.io/badge/SQL Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
            </div>

            <h4>Tools & Others</h4>
            <div class="badges" align="left">
                <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
                <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
                <img src="https://img.shields.io/badge/VS Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white" alt="VS Code">
                <img src="https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white" alt="Postman">
                <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
                <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
            </div>
        </section>

        <hr>

        <section>
            <h3>📂 Featured Projects</h3>
            
            <div class="project">
                <strong>Booking System</strong><br>
                Description: Web application for booking appointments, reservations, or events.<br>
                Tech: Laravel, MySQL, JavaScript<br>
                Highlights: Role-based access, real-time booking updates, notifications
            </div>

            <div class="project">
                <strong><a href="https://github.com/MohamedTBadr/Food-Delievery-APIs">Food Delivery System</a></strong><br>
                Description: Complete food ordering and delivery platform with user-friendly interface.<br>
                Tech: ASP.NET Core, EF Core, SQL Server<br>
                Highlights: Online ordering, order tracking, admin dashboard
            </div>

            <div class="project">
                <strong><a href="https://github.com/MohamedTBadr/job-backOffice">Job Portal</a></strong><br>
                Description: Platform connecting job seekers and employers with job management features.<br>
                Tech: Laravel, MySQL, JavaScript<br>
                Highlights: User authentication, job posting, search and filtering, resume upload
            </div>
        </section>

        <hr>

        <section>
            <h3>📫 Contact Me</h3>
            <ul class="muted">
                <li>LinkedIn: <a href="https://linkedin.com/in/mohamed-tarek-271153262/">Mohamed Tarek</a></li>
                <li>Email: <a href="mailto:mohamedtarekbadr047@gmail.com">mohamedtarekbadr047@gmail.com</a></li>
            </ul>
            <blockquote>“Strive for continuous improvement, not perfection.”</blockquote>
        </section>
    </div>

</body>

</html>
