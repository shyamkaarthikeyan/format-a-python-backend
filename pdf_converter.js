#!/usr/bin/env node
/**
 * PDFKit + docx Manual Layout Converter
 * Handles IEEE 2-column formatting with full layout control
 */

const fs = require('fs');
const PDFDocument = require('pdfkit');
const { Document } = require('docx');

class IEEE2ColumnPDFConverter {
    constructor() {
        // IEEE 2-column layout constants
        this.pageWidth = 612; // 8.5 inches * 72 points
        this.pageHeight = 792; // 11 inches * 72 points
        this.margin = 54; // 0.75 inches
        this.columnGap = 18; // 0.25 inches
        this.columnWidth = (this.pageWidth - 2 * this.margin - this.columnGap) / 2;
        
        // Current position tracking
        this.currentColumn = 1; // 1 or 2
        this.currentY = this.margin + 60; // Start below header
        this.leftColumnX = this.margin;
        this.rightColumnX = this.margin + this.columnWidth + this.columnGap;
    }

    async convertDocxToPdf(docxBuffer) {
        try {
            console.log('Starting PDFKit + docx manual layout conversion...');
            
            // Parse DOCX content
            const docxContent = await this.parseDocxContent(docxBuffer);
            
            // Create PDF document
            const doc = new PDFDocument({
                size: 'LETTER',
                margins: {
                    top: this.margin,
                    bottom: this.margin,
                    left: this.margin,
                    right: this.margin
                }
            });

            // Create buffer to collect PDF data
            const chunks = [];
            doc.on('data', chunk => chunks.push(chunk));
            
            return new Promise((resolve, reject) => {
                doc.on('end', () => {
                    const pdfBuffer = Buffer.concat(chunks);
                    console.log(`PDF conversion successful, size: ${pdfBuffer.length} bytes`);
                    resolve(pdfBuffer);
                });

                doc.on('error', reject);

                // Render content with 2-column layout
                this.renderContent(doc, docxContent);
                
                // Finalize PDF
                doc.end();
            });

        } catch (error) {
            console.error('PDF conversion failed:', error);
            throw new Error(`PDF conversion failed: ${error.message}`);
        }
    }

    async parseDocxContent(docxBuffer) {
        try {
            // For now, we'll create a simple parser
            // In a full implementation, you'd parse the actual DOCX structure
            return {
                title: "IEEE Document",
                authors: ["Author Name"],
                abstract: "This is the abstract section of the IEEE document.",
                sections: [
                    {
                        heading: "I. INTRODUCTION",
                        content: "This is the introduction section with detailed content that will flow across two columns in proper IEEE format."
                    },
                    {
                        heading: "II. METHODOLOGY", 
                        content: "This section describes the methodology used in the research with proper formatting and layout."
                    }
                ],
                tables: [],
                figures: []
            };
        } catch (error) {
            throw new Error(`DOCX parsing failed: ${error.message}`);
        }
    }

    renderContent(doc, content) {
        // Reset position
        this.currentColumn = 1;
        this.currentY = this.margin + 60;

        // Render title (full width, centered)
        this.renderTitle(doc, content.title);
        
        // Render authors (full width, centered)
        this.renderAuthors(doc, content.authors);
        
        // Start 2-column layout
        this.startTwoColumnLayout(doc);
        
        // Render abstract
        this.renderAbstract(doc, content.abstract);
        
        // Render sections
        content.sections.forEach(section => {
            this.renderSection(doc, section);
        });
        
        // Render tables and figures
        content.tables.forEach(table => {
            this.renderTable(doc, table);
        });
        
        content.figures.forEach(figure => {
            this.renderFigure(doc, figure);
        });
    }

    renderTitle(doc, title) {
        doc.fontSize(14)
           .font('Helvetica-Bold')
           .text(title, this.margin, this.currentY, {
               width: this.pageWidth - 2 * this.margin,
               align: 'center'
           });
        
        this.currentY += 30;
    }

    renderAuthors(doc, authors) {
        const authorText = authors.join(', ');
        doc.fontSize(12)
           .font('Helvetica')
           .text(authorText, this.margin, this.currentY, {
               width: this.pageWidth - 2 * this.margin,
               align: 'center'
           });
        
        this.currentY += 25;
    }

    startTwoColumnLayout(doc) {
        // Draw column separator line (optional)
        const separatorX = this.leftColumnX + this.columnWidth + this.columnGap / 2;
        doc.strokeColor('#CCCCCC')
           .lineWidth(0.5)
           .moveTo(separatorX, this.currentY)
           .lineTo(separatorX, this.pageHeight - this.margin)
           .stroke();
    }

    renderAbstract(doc, abstractText) {
        // Abstract header
        this.addTextToColumn(doc, 'Abstract—', 'Helvetica-Bold', 10);
        
        // Abstract content
        this.addTextToColumn(doc, abstractText, 'Helvetica', 10);
        
        // Add space after abstract
        this.addSpaceToColumn(15);
    }

    renderSection(doc, section) {
        // Section heading
        this.addTextToColumn(doc, section.heading, 'Helvetica-Bold', 10);
        
        // Section content
        this.addTextToColumn(doc, section.content, 'Helvetica', 10);
        
        // Add space after section
        this.addSpaceToColumn(10);
    }

    renderTable(doc, table) {
        // For now, render as text
        // In full implementation, create proper table layout
        this.addTextToColumn(doc, '[TABLE PLACEHOLDER]', 'Helvetica-Oblique', 9);
        this.addSpaceToColumn(15);
    }

    renderFigure(doc, figure) {
        // For now, render as text
        // In full implementation, embed actual images
        this.addTextToColumn(doc, '[FIGURE PLACEHOLDER]', 'Helvetica-Oblique', 9);
        this.addSpaceToColumn(15);
    }

    addTextToColumn(doc, text, font, fontSize) {
        const columnX = this.currentColumn === 1 ? this.leftColumnX : this.rightColumnX;
        
        doc.fontSize(fontSize)
           .font(font);
        
        const textHeight = doc.heightOfString(text, { width: this.columnWidth });
        
        // Check if we need to move to next column or page
        if (this.currentY + textHeight > this.pageHeight - this.margin) {
            if (this.currentColumn === 1) {
                // Move to right column
                this.currentColumn = 2;
                this.currentY = this.margin + 60;
            } else {
                // Move to next page
                doc.addPage();
                this.currentColumn = 1;
                this.currentY = this.margin + 60;
                this.startTwoColumnLayout(doc);
            }
        }
        
        const finalColumnX = this.currentColumn === 1 ? this.leftColumnX : this.rightColumnX;
        
        doc.text(text, finalColumnX, this.currentY, {
            width: this.columnWidth,
            align: 'justify'
        });
        
        this.currentY += textHeight + 5; // Add small spacing
    }

    addSpaceToColumn(space) {
        this.currentY += space;
    }
}

// Main function for command line usage
async function main() {
    try {
        if (process.argv.length < 3) {
            console.error('Usage: node pdf_converter.js <input.docx> [output.pdf]');
            process.exit(1);
        }

        const inputPath = process.argv[2];
        const outputPath = process.argv[3] || inputPath.replace('.docx', '.pdf');

        // Read DOCX file
        const docxBuffer = fs.readFileSync(inputPath);
        
        // Convert to PDF
        const converter = new IEEE2ColumnPDFConverter();
        const pdfBuffer = await converter.convertDocxToPdf(docxBuffer);
        
        // Write PDF file
        fs.writeFileSync(outputPath, pdfBuffer);
        
        console.log(`Conversion completed: ${inputPath} -> ${outputPath}`);
        
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

// Export for use as module
module.exports = { IEEE2ColumnPDFConverter };

// Run if called directly
if (require.main === module) {
    main();
}