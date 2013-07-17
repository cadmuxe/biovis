#include "glpropertyeditor.h"
#include "ui_glpropertyeditor.h"

GLPropertyEditor::GLPropertyEditor(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::GLPropertyEditor)
{
    ui->setupUi(this);
}

GLPropertyEditor::~GLPropertyEditor()
{
    delete ui;
}
