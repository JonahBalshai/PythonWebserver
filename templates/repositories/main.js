function sendChunk(submitFileSlice, fileName, chunk) {
    return new Promise(function(resolve) {
        // Create request
        var request = new XMLHttpRequest();
        // Send to correct file
        request.open("POST", "./api");
        // Set encoding
        request.setRequestHeader('Content-Encoding', document.characterSet);
        // Create the form data
        var formData = new FormData();
        formData.append("tagPOST", 'uploadFile');
        formData.append("fileName", fileName);
        formData.append('filePath', window.location.pathname);
        formData.append("chunkNum", chunk);
        formData.append("payload", submitFileSlice);
        // Get the response
        request.onload = function () {
            if (this.status == 200) {
                resolve(request.response);
            }
        }
        // Send the file
        request.send(formData);
    });
}

function updateWebsiteContents() {
    return new Promise(function(resolve) {
        // Get files via post request then append them to div after successfull login
        // Create request 
        var request = new XMLHttpRequest();
        // Send to correct file
        request.open('POST', '/api', true);
        // Set content type and encoding
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        request.setRequestHeader('Content-Encoding', document.characterSet);
        // Send the contents
        request.send(`tagPOST=repositoryContent&filePath=${window.location.pathname}`);
        // Check response
        request.onreadystatechange = function() {
            if (this.readyState == 4) {
                lines = this.response.split('\n');
                if (lines[0] == 'Files returned.') {
                    // Special case when no files in repository
                    if (lines[1] == '') {
                        repository_files = [];
                    } else {
                        repository_files = lines[1].split(';');
                    }
                    // Reset webpage
                    var file_container = document.querySelector('#file_container');
                    file_container.innerHTML = '';
                    // Cycle through the files and create classes with download button for each of them
                    for (let i = 0; i < repository_files.length; i++) {
                        // Create the form
                        var file_class = document.createElement('form');
                        file_class.classList.add('fileForm');
                        file_class.classList.add('text-center');
                        file_class.classList.add('d-flex');
                        file_class.classList.add('flexrow');
                        file_class.classList.add('justify-content-between');
                        file_class.classList.add('mt-2');
                        file_class.classList.add('mb-2');
 
                        // Create the h1 tag for the file name and append to form
                        var file_div = document.createElement('h1');
                        file_div.classList.add('file');
                        file_div.textContent = `${repository_files[i]}`;
                        file_class.appendChild(file_div);

                        // Create dropdown menu
                        var dropdown = document.createElement('div');
                        dropdown.classList.add('dropdown');

                        file_class.appendChild(dropdown);
                        
                        // Append dropdown button
                        var dropdownButton = document.createElement('button');
                        dropdownButton.classList.add('btn');
                        dropdownButton.classList.add('btn-secondary');
                        dropdownButton.classList.add('dropdown-toggle');
                        dropdownButton.type = 'button';
                        dropdownButton.id = 'dropdownMenuButton2';
                        dropdownButton.setAttribute('data-bs-toggle', 'dropdown');
                        dropdownButton.ariaExpanded = false;

                        dropdown.appendChild(dropdownButton);

                        // Create list for dropdown buttons
                        var dropdownMenu = document.createElement('ul');
                        dropdownMenu.classList.add('dropdown-menu');
                        dropdownMenu.setAttribute('aria-labelledby', 'dropdownMenuButton2');

                        dropdown.appendChild(dropdownMenu);

                        // Create download button
                        var file_download_list = document.createElement('li');
                        var file_download = document.createElement('button');
                        file_download.classList.add('dropdown-item');
                        file_download.classList.add('downloadButton');
                        file_download.textContent = 'Download';
                        file_download.setAttribute('onclick', `location.href='/content/${repository_files[i]}'`);

                        file_download_list.appendChild(file_download);
                        dropdownMenu.appendChild(file_download_list);

                        // Create delete button
                        var file_delete_list = document.createElement('li');
                        var file_delete = document.createElement('button');
                        file_delete.id = `${repository_files[i]}`
                        file_delete.classList.add('dropdown-item');
                        file_delete.classList.add('deleteButton');
                        file_delete.textContent = 'Delete';
                        
                        file_delete_list.appendChild(file_delete);
                        dropdownMenu.appendChild(file_delete_list);

                        file_container.appendChild(file_class);
                    }
                    document.body.appendChild(file_container);
                    var script = document.body.querySelector('#scriptTag');
                    document.body.appendChild(script)
                }
                buttonEventListeners();
                resolve();
            }
        };
    });
}

function buttonEventListeners() {
    var downloadButtons = document.getElementsByClassName('downloadButton');

    for (let element of downloadButtons) {
        element.addEventListener('click', async e => {
            e.preventDefault();
        });
    }

    var deleteButtons = document.getElementsByClassName('deleteButton');

    for (let element of deleteButtons) {
        element.addEventListener('click', async e => {
            e.preventDefault();
            // Create request
            var request = new XMLHttpRequest();
            // Send to correct file
            request.open('POST', '/api', true);
            // Set content type and encoding
            request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            request.setRequestHeader('Content-Encoding', document.characterSet);
            // Send the contents
            request.send(`tagPOST=deleteFile&fileName=${element.id}&filePath=${window.location.pathname}`);
            // Check the response
            request.onreadystatechange = function() {
                if (this.readyState == 4) {
                    if (this.response == 'Successfully deleted') {
                        document.getElementById('file_container').removeChild(element.parentNode.parentNode.parentNode.parentNode);
                    }
                }
            }
        });
    };
}

document.addEventListener("DOMContentLoaded", async function() {
    await updateWebsiteContents();

    const uploadForm = document.querySelector("#uploadFile");
    // Define upload button behavior
    uploadForm.addEventListener("submit", async e => {
        e.preventDefault();
        var button = document.getElementById('form__button');
        button.disabled = true;
        
        var submitFile = document.getElementById("form__file").files[0];
        var fileName = submitFile.name;
        var chunkSize = 1024 * 1024;
        var fileSize = submitFile.size;
        var chunks = Math.ceil(fileSize/chunkSize,chunkSize);
        var chunk = 0;

        var progressbar = document.getElementById('file_progressbar');

        if (document.getElementById("form__file").files.length === 0) {
            setFormMessage(uploadForm, "error", "Please select a file")
        } else {
            for (chunk = 0; chunk < chunks; chunk ++) {
                // Set offset
                var offset = chunk*chunkSize;
                // Split the file
                submitFileSlice = submitFile.slice(offset,offset + chunkSize);
                // Await response
                var response = await sendChunk(submitFileSlice, fileName, chunk);
                // Work with response
                lines = response.split('\n');
                // Check if filename needs to be changed
                if (lines[0] == 'Changed filename.') {
                    fileName = lines[1];
                }
                var percentage = ((chunk+1)/chunks)*100;
                progressbar.style.width=`${percentage}%`;
                progressbar.ariaValueNow = percentage
            }
            setTimeout(() => {
                progressbar.classList.add('notransition'); 
                progressbar.ariaValueNow = 0;
                progressbar.style.width='0%';
                progressbar.offsetHeight;
                progressbar.classList.remove('notransition');
            }, 500);
        }
        // Refresh the website
        await updateWebsiteContents();
        // TODO: clear filename of fileupload form
        document.getElementById('form__file').value = '';
        button.disabled = false;
    });
});