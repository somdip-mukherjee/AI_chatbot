const fs = require('fs');
const path = require('path');
const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
app.use(cors());
app.use('/uploads', express.static('uploads'));
app.use('/downloads', express.static('downloads')); // Serve files from 'downloads' folder

// Ensure the uploads and downloads folders exist
const uploadDir = path.join(__dirname, 'uploads');
const downloadDir = path.join(__dirname, 'downloads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
if (!fs.existsSync(downloadDir)) fs.mkdirSync(downloadDir);

const upload = multer({
  storage: multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
      cb(null, file.originalname); // Save with original name
    }
  })
});

app.post('/upload', upload.fields([{ name: 'file1' }, { name: 'file2' }]), (req, res) => {
  const file1Path = req.files.file1[0].path;
  const file2Path = req.files.file2[0].path;

  const outputFilename = `classification_report_${Date.now()}.csv`;
  const outputPath = path.join(downloadDir, outputFilename);

  console.log("output path is ",outputPath);
  const generatedCsvPath = path.join(__dirname, 'classification_report.csv'); // Python writes here

  const python = spawn('python', ['Algorithm/app.py', file1Path, file2Path]);

  python.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  python.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  python.on('close', (code) => {
    console.log(`child process exited with code ${code}`);

    if (code === 0) {
      // Move the CSV file from Python output to the downloads folder
      fs.rename(generatedCsvPath, outputPath, (err) => {
        if (err) {
          console.error('Error moving CSV file:', err);
          return res.status(500).json({ success: false, message: 'Failed to move CSV file' });
        }

        // Respond with download filename
        res.json({ success: true, filename: outputFilename });
        console.log(outputFilename);

        // Delete the uploaded files after sending response
        [file1Path, file2Path].forEach(filePath => {
          fs.unlink(filePath, err => {
            if (err) console.error(`Error deleting ${filePath}:`, err);
            else console.log(`Deleted ${filePath}`);
          });
        });
      });
    } else {
      res.status(500).json({ success: false, message: 'Python script failed' });
    }
  });
});

app.listen(5000, () => {
  console.log('App started on port 5000');
});
