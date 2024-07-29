document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    socket.on("connect", () => {
        socket.emit("get_diff_list");
    });

    socket.on("diff_list", data => {
        const fileList = document.getElementById("file-list");
        fileList.innerHTML = "";
        data.diffs.forEach(diff => {
            const option = document.createElement("option");
            option.value = diff.name;
            option.textContent = diff.name;
            option.dataset.file1Path = diff.file1_path;
            option.dataset.file2Path = diff.file2_path;
            fileList.appendChild(option);
        });

        fileList.addEventListener("change", () => {
            const selectedOption = fileList.options[fileList.selectedIndex];
            loadReport(selectedOption.value);
            document.getElementById("header").textContent = `${selectedOption.dataset.file1Path} vs ${selectedOption.dataset.file2Path}`;
        });
    });

    socket.on("diff_update", data => {
        const diffs = document.getElementById("diffs");
        diffs.innerHTML = "";
        data.diffs.forEach(diff => {
            const row = document.createElement("tr");
            const typeCell = document.createElement("td");
            const lineCell = document.createElement("td");
            const contentCell = document.createElement("td");

            typeCell.textContent = diff.diff_type;
            typeCell.classList.add(diff.diff_type);
            lineCell.textContent = diff.line_number;
            contentCell.textContent = diff.content;

            row.appendChild(typeCell);
            row.appendChild(lineCell);
            row.appendChild(contentCell);
            diffs.appendChild(row);
        });
    });

    function loadReport(name, page = 1, perPage = 10) {
        socket.emit("load_report", { name, page, per_page: perPage });
    }

    document.getElementById("prevBtn").addEventListener("click", () => {
        // Implement pagination logic to load previous page
    });

    document.getElementById("nextBtn").addEventListener("click", () => {
        // Implement pagination logic to load next page
    });
});