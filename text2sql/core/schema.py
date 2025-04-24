"""Models for representing database schema information."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Column(BaseModel):
    """Represents a database column."""
    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="SQL data type")
    is_nullable: bool = Field(default=True, description="Whether the column can be NULL")
    is_primary: bool = Field(default=False, description="Whether the column is part of primary key")
    is_foreign: bool = Field(default=False, description="Whether the column is a foreign key")
    references: Optional[str] = Field(default=None, description="Referenced table.column if foreign key")
    description: Optional[str] = Field(default=None, description="Column description/comment")


class Table(BaseModel):
    """Represents a database table."""
    name: str = Field(..., description="Table name")
    schema: str = Field(default="public", description="Schema name")
    columns: List[Column] = Field(default_factory=list, description="List of columns")
    description: Optional[str] = Field(default=None, description="Table description/comment")
    primary_keys: List[str] = Field(default_factory=list, description="List of primary key column names")
    foreign_keys: List[str] = Field(default_factory=list, description="List of foreign key column names")
    indexes: List[str] = Field(default_factory=list, description="List of indexed column names")


class DatabaseSchema(BaseModel):
    """Represents the complete database schema."""
    tables: List[Table] = Field(default_factory=list, description="List of tables")
    relationships: List[dict] = Field(default_factory=list, description="List of table relationships")
    last_updated: Optional[str] = Field(default=None, description="Timestamp of last schema update")

    def get_table(self, table_name: str) -> Optional[Table]:
        """Get table by name."""
        for table in self.tables:
            if table.name == table_name:
                return table
        return None

    def get_column(self, table_name: str, column_name: str) -> Optional[Column]:
        """Get column by table and column name."""
        table = self.get_table(table_name)
        if table:
            for column in table.columns:
                if column.name == column_name:
                    return column
        return None 