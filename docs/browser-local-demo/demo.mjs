const SAMPLE_TEXT = `# Synthetic local-only sample
rs12564807\t1\t734462\tAA
rs3131972\t1\t752721\tAG
"rs56116432","chrM","73","tt"
`;

export const MAX_PREVIEW_BYTES = 2 * 1024 * 1024;

export const SUPPORTED_LOCALES = ["de", "en", "es", "zh", "ja", "ru"];

const HEADER_RSID_TOKENS = new Set([
  "rsid",
  "snp",
  "marker",
  "name",
  "rs_id",
  "marker_id",
  "snp_name",
  "variant_id",
]);

const NO_CALL_GENOTYPES = new Set(["--", "-", "00"]);

export const DEMO_TRANSLATIONS = {
  de: {
    pageTitle: "Genotype-to-VCF Pro - Browserlokale Demo",
    eyebrow: "Lokale Vorschau ohne Upload",
    langLabel: "Sprache:",
    heroTitle: "Browserlokale Format-Demo",
    heroLead:
      "Diese statische Demo prüft nur lokal im Browser, ob eine Datei grob zum erwarteten Vier-Spalten-Format passt. Es werden keine Rohdaten hochgeladen, gespeichert oder an APIs gesendet.",
    inputHeading: "Eingabe",
    inputHintPrefix: "Unterstützt lokale 23andMe-artige TSV/CSV-Dateien mit",
    chooseFileButton: "Datei wählen",
    sampleButton: "Synthetisches Beispiel laden",
    clearButton: "Leeren",
    pasteLabel: "Oder Text lokal einfügen",
    analyzeButton: "Lokal prüfen",
    limitsHeading: "Grenzen",
    limitNoVcf: "Keine VCF-Erzeugung im Browser.",
    limitNoUpload: "Keine Genotyp-Uploads und keine Server-Komponente.",
    limitNoDbSnp: "Keine dbSNP-, FASTA- oder Build-Erkennung innerhalb der Demo.",
    limitPreviewOnly: "Nur Vorschau, Formatcheck und Risiko-Hinweise.",
    cliHintPrefix: "Für echte Konvertierung bitte weiter die Desktop-App oder die CLI",
    cliHintSuffix: "verwenden.",
    resultHeading: "Ergebnis",
    statusIdle: "Noch nichts geprüft.",
    statusOk:
      "Lokaler Check abgeschlossen: kompatible Vier-Spalten-Zeilen erkannt, ohne Upload oder Netzverkehr.",
    statusWarn:
      "Lokaler Check abgeschlossen: Datei ist nur teilweise oder nicht im erwarteten Vier-Spalten-Format.",
    statusReadError: "Datei konnte lokal im Browser nicht gelesen werden.",
    tableCaption: "Vorschau der erkannten Genotyp-Zeilen",
    colChromosome: "Chromosom",
    colPosition: "Position",
    colGenotype: "Genotyp",
    emptyIdle: "Noch keine Vorschau vorhanden.",
    emptyNoCompatible: "Keine kompatiblen Vier-Spalten-Zeilen gefunden.",
    cardRecognized: "Erkannte Varianten",
    cardSkippedHeaders: "Übersprungene Header",
    cardUnsupported: "Nicht unterstützte Zeilen",
    cardChromosomes: "Chromosomen-Snapshot",
    warnUnsupported:
      "Mindestens eine Zeile hatte nicht genau vier Spalten. Das deutet auf ein nicht unterstütztes Exportformat wie AncestryDNA oder auf kaputte CSV/TSV-Zeilen hin.",
    warnFiveColumn:
      "Mindestens eine Zeile hatte nicht genau vier Spalten (5-Spalten-Layout wie bei AncestryDNA mit getrennten Allelen erkannt). Dieses Tool verarbeitet nur Vier-Spalten-Exporte.",
    warnInvalidPosition:
      "Mindestens eine Zeile enthielt keine ganzzahlige Chromosomenposition und wurde übersprungen.",
    warnNoRecords: "Es wurde kein kompatibler Datensatz erkannt.",
    warnTruncated:
      "Große Datei erkannt: Für flüssige Browser-Darstellung wurde nur eine lokale Stichprobe der ersten 2 MiB geprüft.",
    warnReadOnly:
      "Die Demo bleibt read-only. Für echte VCF-Erzeugung, Build-Erkennung und FASTA/dbSNP-Pfade weiter Desktop-App oder CLI nutzen.",
  },
  en: {
    pageTitle: "Genotype-to-VCF Pro - Browser-Local Demo",
    eyebrow: "Local preview without upload",
    langLabel: "Language:",
    heroTitle: "Browser-Local Format Preflight",
    heroLead:
      "This static demo checks locally in your browser whether a file matches the expected four-column genotype layout. No raw data is uploaded, stored, or sent to any API.",
    inputHeading: "Input",
    inputHintPrefix: "Supports local 23andMe-style TSV/CSV files with",
    chooseFileButton: "Choose file",
    sampleButton: "Load synthetic sample",
    clearButton: "Clear",
    pasteLabel: "Or paste text locally",
    analyzeButton: "Check locally",
    limitsHeading: "Boundaries",
    limitNoVcf: "No VCF generation in the browser.",
    limitNoUpload: "No genotype uploads and no server component.",
    limitNoDbSnp: "No dbSNP, FASTA, or build detection inside this demo.",
    limitPreviewOnly: "Read-only preview, format preflight, and layout warnings only.",
    cliHintPrefix: "For actual VCF conversion, please use the desktop app or headless CLI",
    cliHintSuffix: "locally.",
    resultHeading: "Result",
    statusIdle: "Nothing checked yet.",
    statusOk:
      "Local check complete: compatible four-column rows detected without upload or network traffic.",
    statusWarn:
      "Local check complete: file is only partially or not in the expected four-column format.",
    statusReadError: "Could not read the selected file locally in the browser.",
    tableCaption: "Preview of recognized genotype rows",
    colChromosome: "Chromosome",
    colPosition: "Position",
    colGenotype: "Genotype",
    emptyIdle: "No preview available yet.",
    emptyNoCompatible: "No compatible four-column rows found.",
    cardRecognized: "Recognized variants",
    cardSkippedHeaders: "Skipped headers",
    cardUnsupported: "Unsupported rows",
    cardChromosomes: "Chromosome snapshot",
    warnUnsupported:
      "At least one row did not have exactly four columns. This usually indicates an unsupported export format such as AncestryDNA or malformed CSV/TSV rows.",
    warnFiveColumn:
      "At least one row did not have exactly four columns (5-column layout such as AncestryDNA with split alleles detected). This converter only supports four-column exports.",
    warnInvalidPosition:
      "At least one row had a non-integer chromosomal position and was skipped.",
    warnNoRecords: "No compatible genotype records were recognized.",
    warnTruncated:
      "Large file detected: sampled the first 2 MiB locally so the browser tab stays responsive.",
    warnReadOnly:
      "This demo remains read-only. Use the desktop app or CLI for real VCF generation, build detection, and FASTA/dbSNP lookup.",
  },
  es: {
    pageTitle: "Genotype-to-VCF Pro - Demo local en navegador",
    eyebrow: "Vista previa local sin subida",
    langLabel: "Idioma:",
    heroTitle: "Verificación local de formato",
    heroLead:
      "Esta demostración estática comprueba localmente en su navegador si un archivo coincide con el formato esperado de cuatro columnas. No se suben, guardan ni envían datos genéticos a ninguna API.",
    inputHeading: "Entrada",
    inputHintPrefix: "Admite archivos locales TSV/CSV tipo 23andMe con",
    chooseFileButton: "Elegir archivo",
    sampleButton: "Cargar ejemplo sintético",
    clearButton: "Limpiar",
    pasteLabel: "O pegar texto localmente",
    analyzeButton: "Verificar localmente",
    limitsHeading: "Límites",
    limitNoVcf: "Sin generación de archivos VCF en el navegador.",
    limitNoUpload: "Sin subida de genotipos ni componente de servidor.",
    limitNoDbSnp: "Sin detección de dbSNP, FASTA ni ensamblaje dentro de la demo.",
    limitPreviewOnly: "Solo vista previa de lectura, control de formato y avisos.",
    cliHintPrefix: "Para la conversión real a VCF, utilice la aplicación de escritorio o la CLI",
    cliHintSuffix: "localmente.",
    resultHeading: "Resultado",
    statusIdle: "Aún no se ha verificado nada.",
    statusOk:
      "Verificación local completada: filas compatibles de cuatro columnas detectadas sin subida ni red.",
    statusWarn:
      "Verificación local completada: el archivo solo cumple parcialmente o no coincide con las cuatro columnas esperadas.",
    statusReadError: "No se pudo leer el archivo seleccionado localmente en el navegador.",
    tableCaption: "Vista previa de filas de genotipo reconocidas",
    colChromosome: "Cromosoma",
    colPosition: "Posición",
    colGenotype: "Genotipo",
    emptyIdle: "Aún no hay vista previa disponible.",
    emptyNoCompatible: "No se encontraron filas compatibles de cuatro columnas.",
    cardRecognized: "Variantes reconocidas",
    cardSkippedHeaders: "Encabezados omitidos",
    cardUnsupported: "Filas no admitidas",
    cardChromosomes: "Resumen cromosómico",
    warnUnsupported:
      "Al menos una fila no tenía exactamente cuatro columnas. Esto suele indicar un formato no compatible como AncestryDNA o líneas CSV/TSV dañadas.",
    warnFiveColumn:
      "Al menos una fila tenía cinco columnas (como AncestryDNA con alelos separados). Esta herramienta solo admite exportaciones de cuatro columnas.",
    warnInvalidPosition:
      "Al menos una fila contenía una posición cromosómica no numérica y se omitió.",
    warnNoRecords: "No se reconoció ningún registro de genotipo compatible.",
    warnTruncated:
      "Archivo grande detectado: se analizó localmente una muestra de los primeros 2 MiB para mantener fluido el navegador.",
    warnReadOnly:
      "Esta demo es solo de lectura. Para generar VCF reales y detectar el ensamblaje, utilice la aplicación de escritorio o la CLI.",
  },
  zh: {
    pageTitle: "Genotype-to-VCF Pro - 浏览器本地格式预检",
    eyebrow: "零上传本地预览",
    langLabel: "语言：",
    heroTitle: "浏览器本地格式检查演示",
    heroLead:
      "此静态演示仅在浏览器本地检查文件是否符合预期的四列基因型格式。不会上传、存储或向任何 API 发送原始数据。",
    inputHeading: "输入",
    inputHintPrefix: "支持包含以下四列的本地 23andMe 风格 TSV/CSV 文件：",
    chooseFileButton: "选择文件",
    sampleButton: "加载合成示例",
    clearButton: "清空",
    pasteLabel: "或在本地粘贴文本",
    analyzeButton: "本地检查",
    limitsHeading: "边界说明",
    limitNoVcf: "不在浏览器中生成 VCF 文件。",
    limitNoUpload: "不上传基因型数据，无服务器组件。",
    limitNoDbSnp: "演示内不执行 dbSNP、FASTA 或参考基因组版本检测。",
    limitPreviewOnly: "仅提供只读预览、格式预检与兼容性提示。",
    cliHintPrefix: "如需实际生成 VCF，请在本地使用桌面应用或命令行",
    cliHintSuffix: "。",
    resultHeading: "检查结果",
    statusIdle: "尚未执行检查。",
    statusOk: "本地检查完成：已识别兼容的四列数据行，无上传或网络请求。",
    statusWarn: "本地检查完成：文件仅部分符合或不符合预期的四列格式。",
    statusReadError: "无法在浏览器本地读取所选文件。",
    tableCaption: "已识别基因型行预览",
    colChromosome: "染色体",
    colPosition: "位置",
    colGenotype: "基因型",
    emptyIdle: "暂无预览内容。",
    emptyNoCompatible: "未找到兼容的四列数据行。",
    cardRecognized: "已识别变异数",
    cardSkippedHeaders: "已跳过表头",
    cardUnsupported: "不支持的行数",
    cardChromosomes: "染色体概览",
    warnUnsupported:
      "至少有一行不是恰好四列。这通常表示 AncestryDNA 等不受支持的导出格式，或损坏的 CSV/TSV 行。",
    warnFiveColumn:
      "检测到五列格式行（如拆分等位基因的 AncestryDNA 导出）。本工具仅支持四列导出格式。",
    warnInvalidPosition: "至少有一行的染色体位置不是有效整数，已被跳过。",
    warnNoRecords: "未识别到兼容的基因型记录。",
    warnTruncated: "检测到大文件：为保持浏览器流畅，仅在本地抽样检查前 2 MiB 内容。",
    warnReadOnly:
      "此演示保持只读。如需真正的 VCF 转换、版本检测与 FASTA/dbSNP 解析，请使用桌面应用或 CLI。",
  },
  ja: {
    pageTitle: "Genotype-to-VCF Pro - ブラウザローカル形式チェック",
    eyebrow: "アップロード不要のローカルプレビュー",
    langLabel: "言語:",
    heroTitle: "ブラウザローカル形式デモ",
    heroLead:
      "この静的デモは、ファイルが想定される4列の遺伝型形式に一致するかをブラウザ内でのみ確認します。生データのアップロード、保存、API送信は一切行われません。",
    inputHeading: "入力",
    inputHintPrefix: "次の4列を持つローカルの 23andMe 形式 TSV/CSV に対応:",
    chooseFileButton: "ファイルを選択",
    sampleButton: "合成サンプルを読み込む",
    clearButton: "クリア",
    pasteLabel: "またはテキストをローカルに貼り付け",
    analyzeButton: "ローカルで検査",
    limitsHeading: "制限事項",
    limitNoVcf: "ブラウザ内での VCF 生成は行いません。",
    limitNoUpload: "遺伝型のアップロードやサーバー通信はありません。",
    limitNoDbSnp: "デモ内では dbSNP・FASTA・ビルド判定を行いません。",
    limitPreviewOnly: "読み取り専用のプレビュー、形式確認、注意事項のみを表示します。",
    cliHintPrefix: "実際の VCF 変換にはデスクトップアプリまたは CLI",
    cliHintSuffix: "をご利用ください。",
    resultHeading: "検査結果",
    statusIdle: "まだ検査されていません。",
    statusOk:
      "ローカル検査完了: アップロードや通信なしで互換性のある4列データが確認されました。",
    statusWarn:
      "ローカル検査完了: ファイルの一部または全部が想定される4列形式と一致しません。",
    statusReadError: "選択したファイルをブラウザ内で読み込めませんでした。",
    tableCaption: "認識された遺伝型行のプレビュー",
    colChromosome: "染色体",
    colPosition: "位置",
    colGenotype: "遺伝型",
    emptyIdle: "プレビューはまだありません。",
    emptyNoCompatible: "互換性のある4列データが見つかりませんでした。",
    cardRecognized: "認識されたバリアント",
    cardSkippedHeaders: "スキップしたヘッダー",
    cardUnsupported: "非対応の行数",
    cardChromosomes: "染色体スナップショット",
    warnUnsupported:
      "4列ではない行が少なくとも1行ありました。AncestryDNA などの非対応形式または破損した CSV/TSV 行の可能性があります。",
    warnFiveColumn:
      "5列形式の行（アレルが分割された AncestryDNA 形式など）が検出されました。本ツールは4列形式のみに対応しています。",
    warnInvalidPosition: "染色体位置が整数でない行があったためスキップされました。",
    warnNoRecords: "互換性のある遺伝型レコードが認識されませんでした。",
    warnTruncated:
      "大容量ファイルを検出: ブラウザの応答性を保つため、先頭 2 MiB のみをローカルでサンプル検査しました。",
    warnReadOnly:
      "このデモは読み取り専用です。VCF 生成やビルド判定、FASTA/dbSNP 参照にはデスクトップ版または CLI を使用してください。",
  },
  ru: {
    pageTitle: "Genotype-to-VCF Pro - Локальная проверка формата",
    eyebrow: "Локальный просмотр без загрузки в сеть",
    langLabel: "Язык:",
    heroTitle: "Локальная проверка формата в браузере",
    heroLead:
      "Эта статическая демо-страница проверяет только локально в браузере, соответствует ли файл ожидаемому четырёхколоночному формату. Сырые данные никуда не загружаются, не сохраняются и не отправляются в API.",
    inputHeading: "Ввод данных",
    inputHintPrefix: "Поддерживаются локальные TSV/CSV-файлы формата 23andMe с полями",
    chooseFileButton: "Выбрать файл",
    sampleButton: "Загрузить синтетический пример",
    clearButton: "Очистить",
    pasteLabel: "Или вставить текст локально",
    analyzeButton: "Проверить локально",
    limitsHeading: "Ограничения",
    limitNoVcf: "VCF-файл в браузере не создаётся.",
    limitNoUpload: "Нет выгрузки генотипов и нет серверной части.",
    limitNoDbSnp: "В демо нет запросов к dbSNP, FASTA и автоопределения сборки.",
    limitPreviewOnly: "Только предпросмотр, проверка структуры и предупреждения.",
    cliHintPrefix: "Для реальной конвертации в VCF используйте настольное приложение или CLI",
    cliHintSuffix: "локально.",
    resultHeading: "Результат",
    statusIdle: "Проверка ещё не выполнялась.",
    statusOk:
      "Локальная проверка завершена: обнаружены совместимые четырёхколоночные строки без сетевых запросов.",
    statusWarn:
      "Локальная проверка завершена: файл лишь частично соответствует или не соответствует четырёхколоночному формату.",
    statusReadError: "Не удалось локально прочитать выбранный файл в браузере.",
    tableCaption: "Предпросмотр распознанных строк генотипа",
    colChromosome: "Хромосома",
    colPosition: "Позиция",
    colGenotype: "Генотип",
    emptyIdle: "Предпросмотр пока отсутствует.",
    emptyNoCompatible: "Совместимые четырёхколоночные строки не найдены.",
    cardRecognized: "Распознано вариантов",
    cardSkippedHeaders: "Пропущено заголовков",
    cardUnsupported: "Неподдерживаемых строк",
    cardChromosomes: "Сводка по хромосомам",
    warnUnsupported:
      "Как минимум одна строка содержит не четыре столбца. Это указывает на неподдерживаемый формат вроде AncestryDNA или повреждённые строки CSV/TSV.",
    warnFiveColumn:
      "Обнаружены строки из пяти столбцов (например, AncestryDNA с раздельными аллелями). Инструмент поддерживает только четырёхколоночные экспорты.",
    warnInvalidPosition:
      "Как минимум одна строка содержала некорректную целочисленную позицию и была пропущена.",
    warnNoRecords: "Совместимые записи генотипа не обнаружены.",
    warnTruncated:
      "Обнаружен большой файл: для плавной работы браузера локально проверены первые 2 МиБ.",
    warnReadOnly:
      "Демо работает только в режиме чтения. Для создания VCF, определения сборки и работы с FASTA/dbSNP используйте настольное приложение или CLI.",
  },
};

export function resolveDemoLocale(rawLocale, fallback = "de") {
  const safeFallback = SUPPORTED_LOCALES.includes(fallback) ? fallback : "de";
  if (typeof rawLocale !== "string" || !rawLocale.trim()) {
    return safeFallback;
  }
  const normalized = rawLocale.trim().toLowerCase().replace("_", "-");
  const primary = normalized.split("-")[0];
  return SUPPORTED_LOCALES.includes(primary) ? primary : safeFallback;
}

function tDemo(locale, key) {
  const resolved = resolveDemoLocale(locale, "de");
  return (
    DEMO_TRANSLATIONS[resolved]?.[key] ??
    DEMO_TRANSLATIONS.en?.[key] ??
    DEMO_TRANSLATIONS.de?.[key] ??
    key
  );
}

export function slicePreviewText(text, maxChars = MAX_PREVIEW_BYTES, options = {}) {
  const source = typeof text === "string" ? text : String(text ?? "");
  const forceTruncate = Boolean(options?.forceTruncate);
  if (source.length <= maxChars && !forceTruncate) {
    return { text: source, truncated: false };
  }
  let head = source.slice(0, maxChars);
  const lastNewline = head.lastIndexOf("\n");
  if (lastNewline >= 0) {
    return { text: head.slice(0, lastNewline + 1), truncated: true };
  }
  const lastCode = head.charCodeAt(head.length - 1);
  if (lastCode >= 0xd800 && lastCode <= 0xdbff) {
    head = head.slice(0, -1);
  }
  return { text: head, truncated: true };
}

export function splitDelimitedLine(line, delimiter = ",") {
  const fields = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (char === delimiter && !inQuotes) {
      fields.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  fields.push(current);
  return fields;
}

export function splitCsvLine(line) {
  return splitDelimitedLine(line, ",");
}

function normalizeChromosome(rawChromosome) {
  const upper = rawChromosome.trim().toUpperCase();
  const withoutPrefix = upper.startsWith("CHR") ? upper.slice(3) : upper;
  if (withoutPrefix === "M" || withoutPrefix === "26") {
    return "MT";
  }
  if (withoutPrefix === "23" || withoutPrefix === "25") {
    return "X";
  }
  if (withoutPrefix === "24") {
    return "Y";
  }
  return withoutPrefix;
}

function parseLine(line) {
  let fields;
  if (line.includes("\t")) {
    fields = line.split("\t");
  } else if (line.includes(";")) {
    fields = splitDelimitedLine(line, ";");
    if (fields.length === 1 && line.includes(",")) {
      fields = splitCsvLine(line);
    }
  } else {
    fields = splitCsvLine(line);
  }
  return fields.map((field) => field.trim().replace(/^"(.*)"$/u, "$1"));
}

export function parseGenotypeText(text) {
  const result = {
    records: [],
    stats: {
      skippedBlank: 0,
      skippedComment: 0,
      skippedHeader: 0,
      skippedUnsupportedLayout: 0,
      skippedFiveColumnLayout: 0,
      skippedInvalidPosition: 0,
      skippedEmptyGenotype: 0,
      noCallRecords: 0,
    },
  };

  const cleanedText = String(text ?? "").replace(/^\uFEFF/u, "");
  const lines = cleanedText.split(/\r?\n/u);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      result.stats.skippedBlank += 1;
      continue;
    }
    if (line.startsWith("#")) {
      result.stats.skippedComment += 1;
      continue;
    }

    const parts = parseLine(line);
    const firstLower = (parts[0] ?? "").toLowerCase();
    if (HEADER_RSID_TOKENS.has(firstLower) && (parts.length === 4 || parts.length === 5)) {
      result.stats.skippedHeader += 1;
      continue;
    }

    if (parts.length !== 4) {
      result.stats.skippedUnsupportedLayout += 1;
      if (parts.length === 5) {
        result.stats.skippedFiveColumnLayout += 1;
      }
      continue;
    }

    const [rsid, chrom, pos, genotype] = parts;
    if (!/^[1-9]\d*$/u.test(pos)) {
      result.stats.skippedInvalidPosition += 1;
      continue;
    }

    const normalizedGenotype = genotype.trim().toUpperCase();
    if (!normalizedGenotype) {
      // Gleichlauf mit Make23toVCF3.inspect_genotype_file (skipped_empty_genotype).
      result.stats.skippedEmptyGenotype += 1;
      continue;
    }
    if (NO_CALL_GENOTYPES.has(normalizedGenotype.replace(/_/gu, "-"))) {
      result.stats.noCallRecords += 1;
    }

    result.records.push({
      rsid,
      chromosome: normalizeChromosome(chrom),
      position: Number.parseInt(pos, 10),
      genotype: normalizedGenotype,
    });
  }

  return result;
}

export function summarizeRecords(records, stats, locale = "de", options = {}) {
  const chromosomeCounts = new Map();
  for (const record of records) {
    chromosomeCounts.set(
      record.chromosome,
      (chromosomeCounts.get(record.chromosome) ?? 0) + 1,
    );
  }

  const chromosomes = [...chromosomeCounts.entries()]
    .sort((left, right) => left[0].localeCompare(right[0], undefined, { numeric: true }))
    .slice(0, 6)
    .map(([chromosome, count]) => `${chromosome}:${count}`)
    .join(", ");

  const warnings = [];
  if (stats.skippedFiveColumnLayout > 0) {
    warnings.push(tDemo(locale, "warnFiveColumn"));
  } else if (stats.skippedUnsupportedLayout > 0) {
    warnings.push(tDemo(locale, "warnUnsupported"));
  }
  if ((stats.skippedInvalidPosition ?? 0) > 0) {
    warnings.push(tDemo(locale, "warnInvalidPosition"));
  }
  if (options.truncated) {
    warnings.push(tDemo(locale, "warnTruncated"));
  }
  if (records.length === 0) {
    warnings.push(tDemo(locale, "warnNoRecords"));
  }
  warnings.push(tDemo(locale, "warnReadOnly"));

  return {
    cards: [
      { label: tDemo(locale, "cardRecognized"), value: String(records.length) },
      { label: tDemo(locale, "cardSkippedHeaders"), value: String(stats.skippedHeader) },
      { label: tDemo(locale, "cardUnsupported"), value: String(stats.skippedUnsupportedLayout) },
      { label: tDemo(locale, "cardChromosomes"), value: chromosomes || "—" },
    ],
    warnings,
  };
}

export function analyzeText(text, locale = "de", options = {}) {
  const parsed = parseGenotypeText(text);
  return {
    ...parsed,
    summary: summarizeRecords(parsed.records, parsed.stats, locale, options),
  };
}

function renderSummary(container, cards) {
  container.textContent = "";
  for (const card of cards) {
    const node = document.createElement("article");
    node.className = "summary-card";
    const value = document.createElement("strong");
    value.textContent = card.value;
    const label = document.createElement("span");
    label.textContent = card.label;
    node.append(value, label);
    container.appendChild(node);
  }
}

function renderWarnings(container, warnings) {
  container.textContent = "";
  for (const warning of warnings) {
    const node = document.createElement("div");
    node.className = "warning";
    node.textContent = warning;
    container.appendChild(node);
  }
}

function renderPreview(body, records, locale = "de") {
  body.textContent = "";
  if (records.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = tDemo(locale, "emptyNoCompatible");
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }
  for (const record of records.slice(0, 12)) {
    const row = document.createElement("tr");
    for (const value of [record.rsid, record.chromosome, String(record.position), record.genotype]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }
    body.appendChild(row);
  }
}

function renderStatus(statusBanner, result, locale = "de") {
  const hasWarnings =
    result.stats.skippedUnsupportedLayout > 0 ||
    result.stats.skippedInvalidPosition > 0 ||
    (result.stats.skippedEmptyGenotype ?? 0) > 0 ||
    result.records.length === 0;
  statusBanner.className = `status ${hasWarnings ? "warn" : "ok"}`;
  statusBanner.textContent = hasWarnings
    ? tDemo(locale, "statusWarn")
    : tDemo(locale, "statusOk");
}

function applyStaticTranslations(locale) {
  document.documentElement.lang = locale;
  document.title = tDemo(locale, "pageTitle");
  for (const element of document.querySelectorAll("[data-i18n]")) {
    const key = element.getAttribute("data-i18n");
    if (key) {
      element.textContent = tDemo(locale, key);
    }
  }
}

function attachDom() {
  const fileInput = document.getElementById("file-input");
  const sampleButton = document.getElementById("sample-button");
  const clearButton = document.getElementById("clear-button");
  const analyzeButton = document.getElementById("analyze-button");
  const langSelect = document.getElementById("lang-select");
  const rawInput = document.getElementById("raw-input");
  const statusBanner = document.getElementById("status-banner");
  const summary = document.getElementById("summary");
  const warnings = document.getElementById("warnings");
  const previewBody = document.getElementById("preview-body");

  let currentLocale = resolveDemoLocale(globalThis.navigator?.language, "de");
  let hasAnalyzed = false;
  let lastTruncated = false;

  if (langSelect) {
    langSelect.value = currentLocale;
  }

  const renderIdle = () => {
    hasAnalyzed = false;
    lastTruncated = false;
    statusBanner.className = "status info";
    statusBanner.textContent = tDemo(currentLocale, "statusIdle");
    summary.textContent = "";
    warnings.textContent = "";
    previewBody.textContent = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = tDemo(currentLocale, "emptyIdle");
    row.appendChild(cell);
    previewBody.appendChild(row);
  };

  const runAnalysis = (options = {}) => {
    hasAnalyzed = true;
    lastTruncated = Boolean(options.truncated);
    const result = analyzeText(rawInput.value, currentLocale, { truncated: lastTruncated });
    renderStatus(statusBanner, result, currentLocale);
    renderSummary(summary, result.summary.cards);
    renderWarnings(warnings, result.summary.warnings);
    renderPreview(previewBody, result.records, currentLocale);
  };

  applyStaticTranslations(currentLocale);
  renderIdle();

  if (langSelect) {
    langSelect.addEventListener("change", () => {
      currentLocale = resolveDemoLocale(langSelect.value, "de");
      applyStaticTranslations(currentLocale);
      if (hasAnalyzed) {
        runAnalysis({ truncated: lastTruncated });
      } else {
        renderIdle();
      }
    });
  }

  analyzeButton.addEventListener("click", () => runAnalysis({ truncated: false }));
  sampleButton.addEventListener("click", () => {
    rawInput.value = SAMPLE_TEXT;
    runAnalysis({ truncated: false });
  });
  clearButton.addEventListener("click", () => {
    rawInput.value = "";
    if (fileInput) {
      fileInput.value = "";
    }
    renderIdle();
  });
  rawInput.addEventListener("input", () => {
    lastTruncated = false;
  });
  fileInput.addEventListener("change", async (event) => {
    const [file] = event.target.files ?? [];
    if (!file) {
      return;
    }
    try {
      const oversampled = file.size > MAX_PREVIEW_BYTES;
      const rawChunk = oversampled
        ? await file.slice(0, MAX_PREVIEW_BYTES).text()
        : await file.text();
      const sliced = slicePreviewText(rawChunk, MAX_PREVIEW_BYTES, {
        forceTruncate: oversampled,
      });
      rawInput.value = sliced.text;
      runAnalysis({ truncated: oversampled || sliced.truncated });
    } catch {
      hasAnalyzed = false;
      statusBanner.className = "status warn";
      statusBanner.textContent = tDemo(currentLocale, "statusReadError");
    }
  });
}

if (typeof document !== "undefined") {
  attachDom();
}
