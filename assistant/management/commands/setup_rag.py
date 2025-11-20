"""
Management command برای راه‌اندازی RAG pipeline
"""

from django.core.management.base import BaseCommand
from assistant.rag import RAGPipeline


class Command(BaseCommand):
    help = 'راه‌اندازی RAG pipeline: تولید schema و ایجاد vector store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-openai',
            action='store_true',
            help='استفاده از OpenAI embeddings به جای Hugging Face',
        )
        parser.add_argument(
            '--model-name',
            type=str,
            default='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            help='نام مدل برای embeddings (پیش‌فرض: multilingual model)',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 شروع راه‌اندازی RAG pipeline...')
        
        try:
            # ایجاد RAG pipeline
            rag = RAGPipeline()
            
            # تولید schema
            self.stdout.write('📄 در حال تولید OpenAPI schema...')
            schema_path = rag.generate_schema()
            self.stdout.write(self.style.SUCCESS(f'✅ Schema تولید شد: {schema_path}'))
            
            # ایجاد embeddings و vector store
            use_huggingface = not options['use_openai']
            model_name = options['model_name']
            
            self.stdout.write('🔢 در حال ایجاد embeddings...')
            if use_huggingface:
                self.stdout.write(f'   استفاده از Hugging Face model: {model_name}')
            else:
                self.stdout.write('   استفاده از OpenAI embeddings')
            
            vector_store = rag.create_embeddings(
                use_huggingface=use_huggingface,
                model_name=model_name
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Vector store ایجاد شد: {rag.vector_store_path}'))
            self.stdout.write(self.style.SUCCESS('🎉 RAG pipeline با موفقیت راه‌اندازی شد!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطا در راه‌اندازی RAG: {str(e)}'))
            raise

